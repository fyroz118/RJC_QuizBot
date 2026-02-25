import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import TOKEN
from database import cursor, conn

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    cursor.execute("""
    INSERT OR IGNORE INTO users(telegram_id, username)
    VALUES(?,?)
    """,(user.id,user.username))

    conn.commit()

    await update.message.reply_text(
        "Medical Quiz Bot Ready!\nType /quiz to start."
    )

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 1")
    q = cursor.fetchone()

    if not q:
        await update.message.reply_text("No questions available.")
        return

    context.user_data["current"] = q

    msg = f"""
{q[4]}

A. {q[5]}
B. {q[6]}
C. {q[7]}
D. {q[8]}
"""

    await update.message.reply_text(msg)

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "current" not in context.user_data:
        return

    q = context.user_data["current"]

    user_ans = update.message.text.upper()
    correct = q[9]

    is_correct = 1 if user_ans == correct else 0

    cursor.execute("""
    INSERT INTO attempts(user_id,question_id,selected,correct)
    VALUES(?,?,?,?)
    """,(update.effective_user.id,q[0],user_ans,is_correct))

    conn.commit()

    if is_correct:
        await update.message.reply_text("✅ Correct")
    else:
        await update.message.reply_text(f"❌ Wrong\nCorrect: {correct}\n{q[10]}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("quiz", quiz))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))

app.run_polling()
