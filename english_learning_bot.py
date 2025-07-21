import os
import json
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app_flask = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

VIDEOS_BY_LEVEL = {
    "A1": ["https://www.youtube.com/watch?v=A1Video1", "https://www.youtube.com/watch?v=A1Video2"],
    "A2": ["https://www.youtube.com/watch?v=A2Video1", "https://www.youtube.com/watch?v=A2Video2"],
    "B1": ["https://www.youtube.com/watch?v=B1Video1", "https://www.youtube.com/watch?v=B1Video2"],
}

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/english100bot.json", scope)
    client = gspread.authorize(creds)
    return client.open(GOOGLE_SHEET_NAME).sheet1

def load_progress():
    sheet = get_sheet()
    records = sheet.get_all_records()
    if not records:
        return {"day": 1, "level": "A1", "passed_tests": 0, "history": []}
    last = records[-1]
    return {
        "day": last["Day"],
        "level": last["Level"],
        "passed_tests": last["PassedTests"],
        "history": json.loads(last["Video"])
    }

def save_progress(progress):
    sheet = get_sheet()
    sheet.append_row([
        progress["day"],
        progress["level"],
        json.dumps(progress["history"]),
        progress["passed_tests"]
    ])

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start := start))
application.add_handler(CommandHandler("lesson", lesson := lesson))

@app_flask.route("/", methods=["GET"])
def index():
    return "Bot is running!"

@app_flask.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return "ok"

# تعيين webhook عند بداية التشغيل
@app_flask.before_first_request
def setup_webhook():
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook/{BOT_TOKEN}"
    application.bot.set_webhook(url=webhook_url)
