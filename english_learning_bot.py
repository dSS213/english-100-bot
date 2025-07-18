
import os
import json
import random
import gspread
import threading
from flask import Flask
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
SERVICE_ACCOUNT_PATH = "/etc/secrets/english100bot.json"

VIDEOS_BY_LEVEL = {
    "A1": ["https://www.youtube.com/watch?v=A1Video1", "https://www.youtube.com/watch?v=A1Video2"],
    "A2": ["https://www.youtube.com/watch?v=A2Video1", "https://www.youtube.com/watch?v=A2Video2"],
    "B1": ["https://www.youtube.com/watch?v=B1Video1", "https://www.youtube.com/watch?v=B1Video2"],
}

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_PATH, scope)
    client = gspread.authorize(creds)
    return client.open(GOOGLE_SHEET_NAME).sheet1

def load_progress():
    sheet = get_sheet()
    records = sheet.get_all_records()
    if not records:
        return {"day": 1, "level": "A1", "passed_tests": 0, "history": []}
    last = records[-1]
    return {"day": last["Day"], "level": last["Level"], "passed_tests": last["PassedTests"], "history": json.loads(last["History"])}

def save_progress(progress):
    sheet = get_sheet()
    sheet.append_row([progress["day"], progress["level"], progress["passed_tests"], json.dumps(progress["history"])])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the 100 Days English Challenge! Use /lesson to get today's video.")

async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    progress = load_progress()
    day, level = progress["day"], progress["level"]
    video = random.choice(VIDEOS_BY_LEVEL[level])
    words = random.sample(["apple", "book", "car", "dog", "egg", "fish", "go", "hat", "ice", "jam"], 5)
    story = f"One day, I saw a {words[0]} next to a {words[1]}. I picked it up, put it in my {words[2]}, and walked to the {words[3]} to get some {words[4]}."
    message = f"📚 Day {day} - Level {level}\n🎥 {video}\n🧠 Words: {', '.join(words)}\n📖 {story}"
    await update.message.reply_text(message)
    progress["day"] += 1
    progress["history"].append({"day": day, "video": video, "level": level})
    if day % 10 == 0:
        test_result = random.choice([True, False])
        if test_result:
            progress["passed_tests"] += 1
            await update.message.reply_text("✅ Passed test! Leveling up.")
            if progress["passed_tests"] == 1: progress["level"] = "A2"
            elif progress["passed_tests"] == 2: progress["level"] = "B1"
        else:
            await update.message.reply_text("❌ Test failed. Repeating level.")
    save_progress(progress)

# Flask server for UptimeRobot ping
app_ping = Flask('')
@app_ping.route('/')
def home():
    return "Bot is running!"

def run_web():
    app_ping.run(host="0.0.0.0", port=8080)

# Run Flask in background
threading.Thread(target=run_web).start()

# Telegram bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("lesson", lesson))
app.run_polling()
