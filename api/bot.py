import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from exams import questions

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

user_question_index = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question_index[update.effective_chat.id] = 0
    await send_question(update, context)

async def send_question(update, context):
    chat_id = update.effective_chat.id
    index = user_question_index.get(chat_id, 0)

    if index >= len(questions):
        await context.bot.send_message(chat_id=chat_id, text="🎉 Exam finished!")
        return

    q = questions[index]
    keyboard = [[opt] for opt in q["options"]]

    await context.bot.send_message(
        chat_id=chat_id,
        text=q["question"],
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    index = user_question_index.get(chat_id, 0)

    if index >= len(questions):
        await context.bot.send_message(chat_id=chat_id, text="No active question. Send /start to begin.")
        return

    correct = questions[index]["answer"]
    text = update.message.text if update.message and update.message.text else ""

    if text == correct:
        await context.bot.send_message(chat_id=chat_id, text="✅ Correct!")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Wrong. Correct answer: {correct}")

    user_question_index[chat_id] += 1
    await send_question(update, context)

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set. See .env.example")
        raise SystemExit("BOT_TOKEN environment variable not set")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))

    webhook_url = os.environ.get("WEBHOOK_URL")
    if webhook_url:
        logger.info("Starting bot in webhook mode")
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", 8000)),
            webhook_url=webhook_url
        )
    else:
        logger.info("Starting bot in polling mode")
        app.run_polling()

if __name__ == "__main__":
    main()