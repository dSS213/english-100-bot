import os
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("secrets/english100bot.json", scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1

app_flask = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# -------------------------- Helpers --------------------------
def get_user_row(user_id):
    try:
        cell = sheet.find(str(user_id))
        return cell.row
    except:
        return None

def init_user(user_id):
    row = get_user_row(user_id)
    if row:
        return row
    sheet.append_row([str(user_id), 1, "A1", 0, ""])  # day, level, quizzes, notes
    return len(sheet.get_all_values())

def save_progress(user_id, day, level, quizzes):
    row = get_user_row(user_id)
    if not row:
        row = init_user(user_id)
    sheet.update(f"B{row}", day)
    sheet.update(f"C{row}", level)
    sheet.update(f"D{row}", quizzes)

def get_user_data(user_id):
    row = get_user_row(user_id)
    if not row:
        init_user(user_id)
        return 1, "A1", 0
    values = sheet.row_values(row)
    return int(values[1]), values[2], int(values[3])

# -------------------------- Handlers --------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_user(update.effective_user.id)
    await update.message.reply_text("👋 Welcome to English 100 Bot! Use /lesson to get your daily lesson.")

async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    day, level, quizzes = get_user_data(user_id)
    video_url = f"https://yourvideos.com/{level}/day{day}.mp4"  # Replace with actual URL pattern
    await update.message.reply_text(f"🎯 Day {day} - Level {level}\n{video_url}")
    
    day += 1
    save_progress(user_id, day, level, quizzes)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    day, level, quizzes = get_user_data(user_id)
    
    # Placeholder quiz logic
    await update.message.reply_text("✅ Quiz: What does 'apple' mean?\nA) تفاحة\nB) سيارة\nC) منزل")
    quizzes += 1
    save_progress(user_id, day, level, quizzes)

async def finaltest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    day, level, quizzes = get_user_data(user_id)
    
    if day < 30:
        await update.message.reply_text("❌ Final test is only available after 30 days.")
        return
    
    # Simulated passing
    next_level = "A2" if level == "A1" else "B1"
    await update.message.reply_text(f"🎉 Congrats! You've been promoted to {next_level}!")
    save_progress(user_id, day, next_level, 0)

# -------------------------- Telegram Webhook --------------------------
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("lesson", lesson))
application.add_handler(CommandHandler("quiz", quiz))
application.add_handler(CommandHandler("finaltest", finaltest))

@app_flask.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

if __name__ == "__main__":
    app_flask.run(port=10000)

