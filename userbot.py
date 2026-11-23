"""
1XBOT Auto-Grabber Userbot (Unencrypted / Plain Source for Testing)
- Dynamically fetches supported bots & their special commands from the Vercel API (`GET /bots`)
- Strict 4-step pipeline:
    1. Bot must exist in API `/bots` list (otherwise ignored)
    2. Bot must have a configured `command` AND message caption must contain that special command
       (ignores normal bot media like harem/profile/collection photos)
    3. Fetch character name via `GET /name/{file_unique_id}`
    4. Wait `GRAB_DELAY` and send `{command}@{bot_handle} {first_name}`
- Includes `.stats`, `.grab on/off`, `.syncbots`, and `.testapi` self-commands.
"""

import asyncio
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message

# Load local .env if present
load_dotenv()

# Python 3.12+ event loop safety
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# =============================================================================
# LOGGING
# =============================================================================
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("GrabberUserbot")

# =============================================================================
# CONFIGURATION
# =============================================================================
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "").strip()
SESSION_STRING = os.getenv("SESSION_STRING", "").strip()

# Deployed Vercel backend API
API_BASE_URL = os.getenv("API_BASE_URL", "https://grabapi.vercel.app").strip().rstrip("/")
API_TIMEOUT = float(os.getenv("API_TIMEOUT", "8.0"))

# How often (seconds) to auto-refresh supported bot list from GET /bots
BOT_SYNC_INTERVAL = float(os.getenv("BOT_SYNC_INTERVAL", "300.0"))

# Delay (seconds) before sending the grab command
GRAB_DELAY = float(os.getenv("GRAB_DELAY", "4.0"))

# Send "/grab@BotUsername name" (True) or "/grab name" (False)
TAG_BOT_IN_COMMAND = os.getenv("TAG_BOT_IN_COMMAND", "true").strip().lower() in ("1", "true", "yes")

# Auto-grab master switch (toggle live with `.grab on` / `.grab off`)
AUTO_GRAB_ENABLED = True

# =============================================================================
# RUNTIME STATE (Populated dynamically from Vercel API `GET /bots`)
# =============================================================================
SUPPORTED_BOTS: Dict[str, Dict[str, Any]] = {}
_last_bots_sync_ts: float = 0.0
_bots_sync_lock: Optional[asyncio.Lock] = None

_http_session: Optional[aiohttp.ClientSession] = None
_seen_messages: Dict[Tuple[int, int], float] = {}
_SEEN_TTL_SECONDS = 60.0

_session_grabs: int = 0
_session_misses: int = 0


async def get_http_session() -> aiohttp.ClientSession:
    """Return a shared async aiohttp session."""
    global _http_session
    if _http_session is None or _http_session.closed:
        timeout = aiohttp.ClientTimeout(total=API_TIMEOUT, connect=4.0)
        _http_session = aiohttp.ClientSession(timeout=timeout)
    return _http_session


def _normalize_commands(raw_cmd: Any) -> List[str]:
    """Normalize API `command` field (string, comma-separated string, or list) into ['/cmd', ...]."""
    if not raw_cmd:
        return []
    items: List[str] = []
    if isinstance(raw_cmd, str):
        items = [part.strip() for part in raw_cmd.split(",") if part.strip()]
    elif isinstance(raw_cmd, (list, tuple)):
        items = [str(part).strip() for part in raw_cmd if str(part).strip()]

    normalized: List[str] = []
    for cmd in items:
        c = cmd if cmd.startswith("/") else f"/{cmd}"
        c = c.lower()
        if c not in normalized:
            normalized.append(c)
    return normalized


async def sync_supported_bots(force: bool = False) -> bool:
    """Fetch supported bots and their special commands from `{API_BASE_URL}/bots`."""
    global SUPPORTED_BOTS, _last_bots_sync_ts, _bots_sync_lock

    now = time.monotonic()
    if not force and SUPPORTED_BOTS and (now - _last_bots_sync_ts) < BOT_SYNC_INTERVAL:
        return True

    if _bots_sync_lock is None:
        _bots_sync_lock = asyncio.Lock()

    async with _bots_sync_lock:
        now = time.monotonic()
        if not force and SUPPORTED_BOTS and (now - _last_bots_sync_ts) < BOT_SYNC_INTERVAL:
            return True

        url = f"{API_BASE_URL}/bots"
        try:
            session = await get_http_session()
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.warning("Failed to sync /bots: HTTP %s", resp.status)
                    return False
                data = await resp.json(content_type=None)

            raw_bots = data.get("bots") if isinstance(data, dict) else None
            if not isinstance(raw_bots, list):
                logger.warning("Invalid /bots payload received from API")
                return False

            updated: Dict[str, Dict[str, Any]] = {}
            for entry in raw_bots:
                if not isinstance(entry, dict):
                    continue
                username = str(entry.get("username") or "").lstrip("@").strip()
                if not username:
                    continue
                commands = _normalize_commands(entry.get("command") or entry.get("commands"))
                updated[username.lower()] = {
                    "username": username,
                    "handle": f"@{username}",
                    "group": str(entry.get("group") or "#"),
                    "commands": commands,
                }

            SUPPORTED_BOTS = updated
            _last_bots_sync_ts = time.monotonic()
            active_count = sum(1 for b in SUPPORTED_BOTS.values() if b["commands"])
            logger.info(
                "Synced %d supported bots from API (%d active with special commands)",
                len(SUPPORTED_BOTS),
                active_count,
            )
            return True
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            logger.warning("Network error syncing /bots: %s", err)
            return False
        except Exception as err:
            logger.error("Unexpected error syncing /bots: %s", err, exc_info=True)
            return False


async def fetch_api_stats() -> Optional[Dict[str, Any]]:
    """Fetch database counts from `{API_BASE_URL}/stats`."""
    try:
        session = await get_http_session()
        async with session.get(f"{API_BASE_URL}/stats") as resp:
            if resp.status != 200:
                return None
            data = await resp.json(content_type=None)
            return data if isinstance(data, dict) else None
    except Exception as err:
        logger.warning("Failed to fetch API /stats: %s", err)
        return None


def match_bot_special_command(caption: str, commands: List[str]) -> Optional[str]:
    """
    Verify that the bot's spawn caption contains one of its special commands
    (e.g. `/grab`, `/guess`, `/catch`) so normal bot media is strictly ignored.
    """
    if not caption or not commands:
        return None
    for cmd in commands:
        pattern = rf"(?<!\w){re.escape(cmd)}(?:@[A-Za-z0-9_]+)?(?=$|[\s,.:;!?)\]`\"'])"
        if re.search(pattern, caption, re.IGNORECASE):
            return cmd
    return None


def _mark_and_check_seen(chat_id: int, message_id: int) -> bool:
    """Return True if this (chat_id, message_id) was already processed recently."""
    now = time.monotonic()
    expired = [k for k, ts in _seen_messages.items() if now - ts > _SEEN_TTL_SECONDS]
    for k in expired:
        _seen_messages.pop(k, None)

    key = (chat_id, message_id)
    if key in _seen_messages:
        return True
    _seen_messages[key] = now
    return False


def extract_media_info(message: Message) -> Tuple[Optional[str], Optional[str]]:
    """Extract (file_unique_id, media_type) from photo, video, or animation."""
    if message.photo:
        return message.photo.file_unique_id, "image"
    if message.video:
        return message.video.file_unique_id, "video"
    if message.animation:
        return message.animation.file_unique_id, "video"
    return None, None


async def lookup_character_name(
    file_unique_id: str,
    bot_username: str,
    media_type: str,
) -> Optional[Dict[str, Any]]:
    """Query the deployed Vercel API: GET /name/{file_unique_id}."""
    url = f"{API_BASE_URL}/name/{file_unique_id}"
    params = {"bot": bot_username, "media_type": media_type}

    try:
        session = await get_http_session()
        async with session.get(url, params=params) as resp:
            if resp.status == 404:
                return None
            if resp.status != 200:
                logger.warning("API HTTP %s for %s", resp.status, file_unique_id)
                return None
            data = await resp.json(content_type=None)
            if isinstance(data, dict) and data.get("name"):
                return data
            return None
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        logger.warning("API request error for %s: %s", file_unique_id, err)
        return None
    except Exception as err:
        logger.error("Unexpected API error: %s", err, exc_info=True)
        return None


# =============================================================================
# PYROGRAM / KURIGRAM CLIENT
# =============================================================================
app = Client(
    name="grabber_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)


@app.on_message(filters.photo | filters.video | filters.animation)
async def auto_grab_handler(client: Client, message: Message) -> None:
    """
    Strict 4-step auto-grab pipeline:
      1. Ensure bot list is synced from API & check if sender bot is supported.
      2. Verify sender bot has a special command configured AND caption contains it.
      3. Lookup character name from API using `file_unique_id`.
      4. Delay and send grab command.
    """
    global _session_grabs, _session_misses

    if not AUTO_GRAB_ENABLED:
        return

    user = message.from_user
    if not user or not user.is_bot or not user.username:
        return

    # Refresh bot list from API if empty or TTL expired
    if not SUPPORTED_BOTS or (time.monotonic() - _last_bots_sync_ts) >= BOT_SYNC_INTERVAL:
        await sync_supported_bots()

    # Step 1: Bot must be in API support list (otherwise ignore)
    bot_cfg = SUPPORTED_BOTS.get(user.username.lower())
    if not bot_cfg:
        return

    # Step 2: Bot must have special command(s) on API AND caption must match it
    caption = message.caption or ""
    matched_command = match_bot_special_command(caption, bot_cfg["commands"])
    if not matched_command:
        return

    # Dedup guard
    if _mark_and_check_seen(message.chat.id, message.id):
        return

    # Extract file_unique_id
    file_unique_id, media_type = extract_media_info(message)
    if not file_unique_id or not media_type:
        return

    bot_username = bot_cfg["username"]
    logger.info(
        "Valid spawn | bot=@%s | cmd=%s | chat=%s | uid=%s (%s)",
        bot_username,
        matched_command,
        message.chat.id,
        file_unique_id,
        media_type,
    )

    # Step 3: Lookup character name from API
    doc = await lookup_character_name(file_unique_id, bot_username, media_type)
    if not doc:
        _session_misses += 1
        logger.info("Character not found in API | uid=%s", file_unique_id)
        return

    full_name = str(doc.get("name", "")).strip()
    first_name = str(doc.get("first_name") or "").strip() or (
        full_name.split()[0].lower() if full_name else ""
    )
    if not first_name:
        return

    # Step 4: Delay & grab
    if GRAB_DELAY > 0:
        await asyncio.sleep(GRAB_DELAY)

    cmd_text = (
        f"{matched_command}@{bot_username} {first_name}"
        if TAG_BOT_IN_COMMAND
        else f"{matched_command} {first_name}"
    )

    try:
        await client.send_message(message.chat.id, cmd_text)
        _session_grabs += 1
        logger.info("Grabbed: %s (full_name=%s)", cmd_text, full_name)
    except FloodWait as fw:
        logger.warning("FloodWait %ss while sending grab command", fw.value)
        await asyncio.sleep(fw.value)
    except RPCError as rpc_err:
        logger.error("Telegram RPCError sending grab command: %s", rpc_err)


# =============================================================================
# USER SELF-COMMANDS
# =============================================================================
@app.on_message(filters.me & filters.command("stats", prefixes=["."]))
async def stats_command(client: Client, message: Message) -> None:
    """Show live API sync status, active working bots, and DB stats."""
    await message.edit("⏳ **Fetching live stats from API...**")

    synced = await sync_supported_bots(force=True)
    api_stats = await fetch_api_stats()

    total_bots = len(SUPPORTED_BOTS)
    active_bots = [b for b in SUPPORTED_BOTS.values() if b["commands"]]
    inactive_bots = [b for b in SUPPORTED_BOTS.values() if not b["commands"]]

    status_label = "ENABLED ✅" if AUTO_GRAB_ENABLED else "DISABLED ⏸️"
    sync_label = "Online ✅" if synced else "Failed ❌"

    lines = [
        "📊 **Auto-Grabber Stats**",
        "",
        f"• **Status:** `{status_label}`",
        f"• **API Sync:** `{sync_label}` (`{API_BASE_URL}`)",
        f"• **Grab Delay:** `{GRAB_DELAY}s`",
        f"• **Session Grabs:** `{_session_grabs}` | **Misses:** `{_session_misses}`",
    ]

    if api_stats:
        lines.append(
            f"• **DB Characters:** `{api_stats.get('total_characters', 0)}` "
            f"(🖼 `{api_stats.get('images', 0)}` | 🎬 `{api_stats.get('videos', 0)}`)"
        )

    lines.append("")
    lines.append(
        f"🤖 **Supported Bots:** `{total_bots}` total | "
        f"**Working (Command Active):** `{len(active_bots)}` | "
        f"**Pending Command:** `{len(inactive_bots)}`"
    )

    if active_bots:
        lines.append("")
        lines.append("✅ **Active Working Bots:**")
        for b in active_bots:
            cmds = ", ".join(b["commands"])
            lines.append(f"  • `{b['handle']}` → `{cmds}`")
    else:
        lines.append("")
        lines.append("⚠️ Abhi API `/bots` me kisi bot ka special `command` set nahi hai, isliye auto-grab idle hai.")

    text = "\n".join(lines)
    if len(text) > 4000:
        text = text[:3960] + "\n\n... *(truncated)*"

    await message.edit(text)


@app.on_message(filters.me & filters.command("grab", prefixes=["."]))
async def toggle_grab_command(client: Client, message: Message) -> None:
    """Toggle auto-grabber: `.grab on` or `.grab off`."""
    global AUTO_GRAB_ENABLED
    arg = message.command[1].lower() if len(message.command) > 1 else ""

    if arg == "on":
        AUTO_GRAB_ENABLED = True
        await message.edit("✅ **Auto-Grabber:** `ENABLED`")
    elif arg == "off":
        AUTO_GRAB_ENABLED = False
        await message.edit("⏸️ **Auto-Grabber:** `DISABLED`")
    else:
        await message.edit(
            f"**Auto-Grabber:** `{'ENABLED' if AUTO_GRAB_ENABLED else 'DISABLED'}`\n"
            "Use `.grab on`, `.grab off`, or `.stats`."
        )


@app.on_message(filters.me & filters.command("syncbots", prefixes=["."]))
async def sync_bots_command(client: Client, message: Message) -> None:
    """Manually refresh supported bot list & commands from API `/bots`."""
    await message.edit("🔄 **Syncing supported bots from API...**")
    ok = await sync_supported_bots(force=True)
    if not ok:
        await message.edit(f"❌ Failed to sync from `{API_BASE_URL}/bots`")
        return

    active_count = sum(1 for b in SUPPORTED_BOTS.values() if b["commands"])
    await message.edit(
        f"✅ **Synced!**\n"
        f"• **Total Bots:** `{len(SUPPORTED_BOTS)}`\n"
        f"• **Working (with command):** `{active_count}`"
    )


@app.on_message(filters.me & filters.command("testapi", prefixes=["."]))
async def test_api_command(client: Client, message: Message) -> None:
    """Reply to any character photo/video with `.testapi` to test API lookup live."""
    reply = message.reply_to_message
    if not reply:
        await message.edit("❌ Reply to a character photo/video with `.testapi`")
        return

    uid, media_type = extract_media_info(reply)
    if not uid or not media_type:
        await message.edit("❌ Replied message has no photo, video, or animation.")
        return

    bot_username = (
        reply.from_user.username
        if reply.from_user and reply.from_user.username
        else "unknown"
    )
    await message.edit(f"🔍 Looking up `{uid}` ({media_type})...")

    doc = await lookup_character_name(uid, bot_username, media_type)
    if not doc:
        await message.edit(f"❌ Not found in DB\n`file_unique_id`: `{uid}`")
        return

    await message.edit(
        "✅ **Character Found**\n"
        f"**Name:** `{doc.get('name')}`\n"
        f"**First Name:** `{doc.get('first_name')}`\n"
        f"**Anime:** `{doc.get('anime', 'Unknown')}`\n"
        f"**Rarity:** `{doc.get('rarity', 'Unknown')}`\n"
        f"**UID:** `{uid}`"
    )


async def _shutdown() -> None:
    global _http_session
    if _http_session and not _http_session.closed:
        await _http_session.close()


if __name__ == "__main__":
    if not API_ID or not API_HASH or not SESSION_STRING:
        logger.error("Set API_ID, API_HASH, and SESSION_STRING environment variables first.")
        raise SystemExit(1)

    logger.info("Starting Grabber Userbot | API=%s | Delay=%ss", API_BASE_URL, GRAB_DELAY)
    try:
        app.run()
    finally:
        try:
            asyncio.run(_shutdown())
        except Exception:
            pass
