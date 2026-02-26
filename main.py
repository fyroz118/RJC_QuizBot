import os
print("TOKEN DEBUG:", os.getenv("TOKEN"))

import csv
import random

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import TOKEN
from database import cursor, conn


# -----------------------------
# Load Questions Automatically
# -----------------------------
def load_questions():
    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]

    # Load only if database is empty
    if count == 0:
        try:
            with open("questions_usmle.csv", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    cursor.execute("""
                    INSERT INTO questions(
                        exam, subject, topic,
                        question,
                        option_a, option_b, option_c, option_d,
                        answer, explanation
                    )
                    VALUES(?,?,?,?,?,?,?,?,?,?)
                    """, (
                        row["exam"],
                        row["subject"],
                        row["topic"],
                        row["question"],
                        row["option_a"],
                        row["option_b"],
                        row["option_c"],
                        row["option_d"],
                        row["answer"],
                        row["explanation"]
                    ))

            conn.commit()
            print("✅ Questions loaded successfully")

        except Exception as e:
            print("❌ Question loading error:", e)


# -----------------------------
# /start command
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    cursor.execute("""
    INSERT OR IGNORE INTO users(telegram_id, username)
    VALUES(?,?)
    """, (user.id, user.username))

    conn.commit()

    await update.message.reply_text(
        "Medical Quiz Bot Ready!\nType /quiz to start."
    )


# -----------------------------
# /quiz command
# -----------------------------
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 1")
    q = cursor.fetchone()

    if not q:
        await update.message.reply_text("No questions available.")
        return

    # Save question in user session
    context.user_data["current"] = q

    msg = f"""
🧠 {q[4]}

A. {q[5]}
B. {q[6]}
C. {q[7]}
D. {q[8]}

Reply with A, B, C or D
"""

    await update.message.reply_text(msg)


# -----------------------------
# Answer Checking
# -----------------------------
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "current" not in context.user_data:
        return

    q = context.user_data["current"]

    user_ans = update.message.text.upper()
    correct = q[9]

    is_correct = 1 if user_ans == correct else 0

    cursor.execute("""
    INSERT INTO attempts(user_id, question_id, selected, correct)
    VALUES(?,?,?,?)
    """, (
        update.effective_user.id,
        q[0],
        user_ans,
        is_correct
    ))

    conn.commit()

    if is_correct:
        await update.message.reply_text("✅ Correct!")
    else:
        await update.message.reply_text(
            f"❌ Wrong\nCorrect Answer: {correct}\n\n{q[10]}"
        )


# -----------------------------
# Bot Setup
# -----------------------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("quiz", quiz))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))


# -----------------------------
# Startup Execution
# -----------------------------
if __name__ == "__main__":
    load_questions()
    app.run_polling()