import os
import asyncio

from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)


telegram_app = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot is running on Vercel 🚀"
    )


telegram_app.add_handler(CommandHandler("start", start))


@app.route("/", methods=["GET"])
def home():
    return "Bot is alive"


@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    async def process():
        await telegram_app.initialize()

        update = Update.de_json(
            data,
            telegram_app.bot,
        )

        await telegram_app.process_update(update)

    asyncio.run(process())

    return "ok"