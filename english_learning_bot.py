
import json
import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

BOT_TOKEN = "7866989610:AAG_faNdNuma8mrYvxJjKoP1I8xkp9p_AlE"
PROGRESS_FILE = "progress.json"

VIDEOS = {
    "A1": [
        {"title": "My Daily Routine", "url": "https://youtu.be/VEjM8ULGkAs"},
        {"title": "Ordering Food", "url": "https://youtu.be/H9Mn9Cwi7oI"},
        {"title": "Talking About Your Job", "url": "https://youtu.be/p7Az-kpEdwM"},
    ],
    "A2": [
        {"title": "Traveling by Plane", "url": "https://youtu.be/3sWY9rY9gis"},
        {"title": "Going to the Doctor", "url": "https://youtu.be/MICzvB1SLnc"},
        {"title": "Describing Your Family", "url": "https://youtu.be/W__IqRxnZjE"},
    ],
    "B1": [
        {"title": "How to Be More Productive", "url": "https://youtu.be/MptJrdUj3ps"},
        {"title": "Making Big Life Decisions", "url": "https://youtu.be/q2jxYy37MAg"},
        {"title": "Habits That Improve Your Life", "url": "https://youtu.be/oyRJ-odYYvM"},
    ]
}

KEYWORDS = {
    "My Daily Routine": ["wake", "eat", "go", "work", "sleep"],
    "Ordering Food": ["menu", "order", "waiter", "dish", "bill"],
    "Talking About Your Job": ["job", "office", "boss", "meeting", "project"],
    "Traveling by Plane": ["airport", "passport", "ticket", "flight", "luggage"],
    "Going to the Doctor": ["pain", "appointment", "medicine", "sick", "rest"],
    "Describing Your Family": ["mother", "father", "sister", "brother", "family"],
    "How to Be More Productive": ["focus", "plan", "goal", "routine", "time"],
    "Making Big Life Decisions": ["choice", "risk", "future", "change", "career"],
    "Habits That Improve Your Life": ["habit", "healthy", "daily", "growth", "discipline"],
}

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {"day": 1, "level": "A1", "history": [], "passed_tests": 0}
    with open(PROGRESS_FILE, "r") as f:
        return json.load(f)

def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)

def generate_story(words):
    return f"Today, I will {words[0]} and then {words[1]}. Later, I will {words[2]} with my {words[3]}, before I finally {words[4]}."

async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    progress = load_progress()
    level = progress["level"]
    day = progress["day"]

    video = random.choice(VIDEOS[level])
    words = KEYWORDS[video["title"]]
    story = generate_story(words)

    msg = f"Day {day} - Level {level}\nTitle: {video['title']}\nLink: {video['url']}\n\nWords: {', '.join(words)}\n\nStory:\n{story}\n\nPractice reading the story aloud in front of a mirror."
    await update.message.reply_text(msg)

    progress["history"].append({"day": day, "video": video["title"], "level": level})
    progress["day"] += 1

    if progress["day"] % 10 == 1:
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

    message = f"Progress:\nDay: {day}\nLevel: {level}\nPassed Reviews: {passed}\n\nLesson History (last 5 days):"
    for entry in history[-5:]:
        message += f"\n- Day {entry['day']}: {entry['video']} ({entry['level']})"

    await update.message.reply_text(message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the 100 Days English Challenge! Use /lesson to get today's video.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("lesson", lesson))
app.add_handler(CommandHandler("progress", progress_command))
app.run_polling()
