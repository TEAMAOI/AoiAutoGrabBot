# ⚡ Grabber Userbot

<p align="center">
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">
</p>

An async Telegram **Character Auto-Grabber Userbot** built with **Kurigram/Pyrogram** and **aiohttp**, dynamically powered by the **Grabber Vercel API** (`https://grabapi.vercel.app`).

## 🚀 One-Click Deploy on Aoi Hosting

[![Deploy on Aoi Hosting](https://host-repository.vercel.app/deploy-button.svg)](https://host-repository.vercel.app/deploy?template=https://github.com/OWNER/REPO)

> **Note:** After pushing this repo to GitHub, replace `OWNER/REPO` in the button URL above (and in `app.json`) with your actual GitHub `username/repo`.

## ✨ Features

- **API-Driven Bot List & Commands**: Automatically syncs supported bots and their exact special commands (`/grab`, `/guess`, `/catch`, etc.) from `GET /bots`.
- **Strict Spawn Verification**: Ignores unsupported bots and normal bot media (harem, profile, gift, etc.) unless the caption contains that bot's configured special command.
- **Photo, Video & GIF Support**: Resolves `file_unique_id` for both images and videos/animations via `GET /name/{file_unique_id}`.
- **Live Self-Commands**:
  - `.stats` — Shows live API sync status, DB counts, and how many supported bots are currently active/working with commands.
  - `.grab on` / `.grab off` — Enable or pause auto-grabbing live.
  - `.syncbots` — Force-refresh the supported bots list from the API.
  - `.testapi` — Reply to any character photo/video to test API lookup directly.

## 📁 Project Structure

```text
grabber-userbot/
├── userbot.py        # Main async Kurigram/Pyrogram userbot
├── aoi.json          # Aoi Hosting one-click deployment manifest
├── app.json          # Heroku / compatible deployment manifest
├── Dockerfile        # Docker container config
├── Procfile          # Worker process declaration
├── runtime.txt       # Python runtime version
├── requirements.txt  # Minimal Python dependencies
├── .env.example      # Environment variable template
└── README.md         # Setup & deployment guide
```

## 🛠️ Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure environment variables**:
   Copy `.env.example` to `.env` and fill in `API_ID`, `API_HASH`, and `SESSION_STRING`.
3. **Run the userbot**:
   ```bash
   python3 userbot.py
   ```

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
| :--- | :---: | :--- | :--- |
| `API_ID` | Yes | — | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Yes | — | Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `SESSION_STRING` | Yes | — | Pyrogram/Kurigram String Session |
| `API_BASE_URL` | No | `https://grabapi.vercel.app` | Grabber Vercel API base URL |
| `GRAB_DELAY` | No | `4.0` | Delay in seconds before sending grab command |
| `BOT_SYNC_INTERVAL` | No | `300.0` | Auto-refresh interval for `/bots` (seconds) |
| `TAG_BOT_IN_COMMAND` | No | `true` | Send `/cmd@BotUsername name` (`true`) or `/cmd name` (`false`) |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity (`INFO`, `DEBUG`, `WARNING`) |

## 🌐 Community & Support

- **Telegram Channel:** [@aoinetwork](https://t.me/aoinetwork)
- **Support Group:** [@devpointserror](https://t.me/devpointserror)
