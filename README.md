# English 100 Bot

A Telegram bot to teach English over 100 days with level progression and automatic tracking via Google Sheets.

## Features
- Daily lessons with video
- Progress tracking
- Mini-tests every 10 days
- Full tests every 30 days to advance levels
- Google Sheets integration

## Running Locally

1. Create `.env` file with:
   ```
   BOT_TOKEN=your_bot_token_here
   GOOGLE_SHEET_NAME=your_google_sheet_name
   ```

2. Add `english100bot.json` to `secrets/` folder.

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run locally:
   ```
   python english_learning_bot.py
   ```

5. Use ngrok and set your webhook:
   ```
   ngrok http 10000
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://xxxx.ngrok.io/webhook/<YOUR_BOT_TOKEN>
   ```

## Deploy on Render

1. Push files to GitHub.
2. Create new Web Service on Render.
3. Set build command (leave empty) and start command is handled by `Procfile`.
4. Add environment variables:
   - `BOT_TOKEN`
   - `GOOGLE_SHEET_NAME`
5. Upload `english100bot.json` via **Secrets** to `/secrets/english100bot.json`.
6. Set webhook:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-app-name.onrender.com/webhook/<YOUR_BOT_TOKEN>
   ```

Enjoy learning English! 🎓
