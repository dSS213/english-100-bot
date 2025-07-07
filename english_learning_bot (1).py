
import os
import json
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

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

PROGRESS_FILE = "progress.json"

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {"day": 1, "level": "A1", "passed_tests": 0, "history": []}
    with open(PROGRESS_FILE, "r") as f:
        return json.load(f)

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

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
