import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from exams import questions

BOT_TOKEN = os.environ.get("BOT_TOKEN")

user_question_index = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question_index[update.effective_chat.id] = 0
    await send_question(update, context)

async def send_question(update, context):
    chat_id = update.effective_chat.id
    index = user_question_index.get(chat_id, 0)

    if index >= len(questions):
        await update.message.reply_text("🎉 Exam finished!")
        return

    q = questions[index]
    keyboard = [[opt] for opt in q["options"]]

    await update.message.reply_text(
        q["question"],
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    index = user_question_index.get(chat_id, 0)

    correct = questions[index]["answer"]

    if update.message.text == correct:
        await update.message.reply_text("✅ Correct!")
    else:
        await update.message.reply_text(f"❌ Wrong. Correct answer: {correct}")

    user_question_index[chat_id] += 1
    await send_question(update, context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        webhook_url=os.environ.get("WEBHOOK_URL")
    )

if __name__ == "__main__":
    main()
