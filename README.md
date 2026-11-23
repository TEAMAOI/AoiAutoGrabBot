# ⚡ Grabber Userbot

<p align="center">
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">
</p>

An async Telegram **Character Auto-Grabber Userbot** built with **Kurigram/Pyrogram**, **aiohttp**, and **MongoDB**.

## 🚀 One-Click Deploy on Aoi Hosting

[![Deploy on Aoi Hosting](https://host-repository.vercel.app/deploy-button.svg)](https://host-repository.vercel.app/deploy?template=https://github.com/TEAMAOI/AoiAutoGrabBot)

- **GitHub Repository:** [TEAMAOI/AoiAutoGrabBot](https://github.com/TEAMAOI/AoiAutoGrabBot)

## ✨ Features

- **Per-Bot ON/OFF Control (MongoDB Persistent)**: All bots start **OFF** by default. Enable only the bots you want with `.on <username>` and disable anytime with `.off <username>` — saved safely in your own MongoDB.
- **Automatic Multi-Bot Support**: Syncs supported bots and their special spawn commands automatically.
- **Strict Spawn Verification**: Ignores disabled bots, unsupported bots, and normal bot media unless the caption contains that bot's special command.
- **Photo, Video & GIF Support**: Automatically identifies both image and video/GIF character spawns.

## 📜 Commands

| Command | Description |
| :--- | :--- |
| `.help` | Show all commands and repository link |
| `.stats` | Show alive status, session grabs, and your enabled bots |
| `.botslist` | List all supported working bots with their `ON` / `OFF` status |
| `.on <username>` | Enable auto-grab for a specific bot (or `.on all`) |
| `.off <username>` | Disable auto-grab for a specific bot (or `.off all`) |
| `.grab on` / `.grab off` | Master switch to enable or pause auto-grabbing |
| `.syncbots` | Force-refresh the supported bots list |
| `.testapi` | Reply to any character photo/video to test lookup |

## 📁 Project Structure

```text
grabber-userbot/
├── userbot.py        # Encrypted async Kurigram/Pyrogram userbot
├── aoi.json          # Aoi Hosting one-click deployment manifest
├── app.json          # Heroku / compatible deployment manifest
├── Dockerfile        # Docker container config
├── Procfile          # Worker process declaration
├── runtime.txt       # Python runtime version
├── requirements.txt  # Python dependencies
├── .env.example      # Environment variable template
└── README.md         # Setup & deployment guide
```

## 🛠️ Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure environment variables**:
   Copy `.env.example` to `.env` and fill in `API_ID`, `API_HASH`, `SESSION_STRING`, and `MONGO_URI`.
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
| `MONGO_URI` | Yes | — | Your own MongoDB URI for saving per-bot ON/OFF settings |
| `GRAB_DELAY` | No | `4.0` | Delay in seconds before sending grab command |
| `TAG_BOT_IN_COMMAND` | No | `true` | Send `/cmd@BotUsername name` (`true`) or `/cmd name` (`false`) |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity (`INFO`, `DEBUG`, `WARNING`) |

## 🌐 Community & Support

- **Open Source Repo:** [https://github.com/TEAMAOI/AoiAutoGrabBot](https://github.com/TEAMAOI/AoiAutoGrabBot)
- **Telegram Channel:** [@aoinetwork](https://t.me/aoinetwork)
- **Support Group:** [@devpointserror](https://t.me/devpointserror)
