import os
import json
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

VIDEOS_BY_LEVEL = {
    "A1": [
        "https://www.youtube.com/watch?v=A1Video1",
        "https://www.youtube.com/watch?v=A1Video2",
        "https://www.youtube.com/watch?v=A1Video3",
    ],
    "A2": [
        "https://www.youtube.com/watch?v=A2Video1",
        "https://www.youtube.com/watch?v=A2Video2",
        "https://www.youtube.com/watch?v=A2Video3",
    ],
    "B1": [
        "https://www.youtube.com/watch?v=B1Video1",
        "https://www.youtube.com/watch?v=B1Video2",
        "https://www.youtube.com/watch?v=B1Video3",
    ],
}

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("english100bot.json", scope)
    client = gspread.authorize(creds)
    return client.open(GOOGLE_SHEET_NAME).sheet1

def load_progress():
    try:
        sheet = get_sheet()
        records = sheet.get_all_records()
        if not records:
            return {"day": 1, "level": "A1", "passed_tests": 0, "history": []}
        last = records[-1]
        return {
            "day": last["day"],
            "level": last["level"],
            "passed_tests": last["passed_tests"],
            "history": json.loads(last["history"])
        }
    except:
        return {"day": 1, "level": "A1", "passed_tests": 0, "history": []}

def save_progress(progress):
    sheet = get_sheet()
    sheet.append_row([
        progress["day"],
        progress["level"],
        progress["passed_tests"],
        json.dumps(progress["history"])
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the 100 Days English Challenge! Use /lesson to get today's video.")

async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    progress = load_progress()
    day = progress["day"]
    level = progress["level"]
    video = random.choice(VIDEOS_BY_LEVEL[level])
    words = random.sample(["apple", "book", "car", "dog", "egg", "fish", "go", "hat", "ice", "jam"], 5)
    story = f"One day, I saw a {words[0]} next to a {words[1]}. I picked it up, put it in my {words[2]}, and walked to the {words[3]} to get some {words[4]}."
    message = f"📚 Day {day} - Level {level}

🎥 Today's video: {video}

🧠 Words to learn: {', '.join(words)}

📖 Story:
{story}

🪞 Read this story aloud in front of a mirror."
    await update.message.reply_text(message)
    progress["day"] += 1
    progress["history"].append({"day": day, "video": video, "level": level})

    if day % 10 == 0:
        test_result = random.choice([True, False])
        if test_result:
            progress["passed_tests"] += 1
            await update.message.reply_text("✅ You passed the review test. Leveling up.")
        else:
            await update.message.reply_text("❌ You did not pass the review. Repeating the level.")

        if progress["passed_tests"] == 1 and progress["day"] > 10:
            progress["level"] = "A2"
        elif progress["passed_tests"] == 2 and progress["day"] > 30:
            progress["level"] = "B1"

    save_progress(progress)

async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    progress = load_progress()
    day = progress["day"]
    level = progress["level"]
    passed = progress["passed_tests"]
    history = progress["history"]
    message = f"📊 Progress:\nDay: {day}\nLevel: {level}\nPassed Reviews: {passed}\n\nLesson History (last 5 days):"
    for entry in history[-5:]:
        message += f"\n- Day {entry['day']}: {entry['video']} ({entry['level']})"
    await update.message.reply_text(message)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("lesson", lesson))
app.add_handler(CommandHandler("progress", progress_command))
app.run_polling()