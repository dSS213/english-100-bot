# 🧠 English 100 Bot — Telegram Bot for Learning English in 100 Days

## 🎯 Idea
This Telegram bot helps users learn English over 100 days. It sends a daily video based on the user's level, starting from A1 and automatically progressing to A2 and B1 every 10 days.

## ✅ Features
- Sends a **daily educational video**.
- Tracks user progress using **Google Sheets**:
  - Day number
  - Current level
  - Video history
  - Number of passed tests
- **Automatically increases level** every 10 days if user passes the test.
- **Persistent progress**: does not reset if bot restarts or moves to another server/device.

## ⚙️ Technical Stack
- `python-telegram-bot` v20+ (no `Updater`, no `update_queue`)
- `application.process_update(update)` for Webhook support
- **Flask** for Webhook server
- **Render.com** for cloud deployment using `gunicorn`
- **Google Sheets API** via `gspread` and `oauth2client` for progress storage

## 🚫 Common Issues Solved
- Fixed bugs caused by mixing old PTB code (`Updater`, `update_queue`) with version 20+.
- Ensured full Webhook compatibility for cloud deployment.

## 🔐 Secrets & Security
- Google API credentials stored securely at `/etc/secrets/english100bot.json`
- Bot token read from environment variable `BOT_TOKEN`

---

🎉 The project is now fully functional and deployable on Render with stable webhook support and persistent progress tracking.
