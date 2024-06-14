import logging
import os

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from telegram.ext import (
    ContextTypes,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram import Update
from asgiref.sync import sync_to_async

# Встановлення налаштувань Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")
django.setup()

User = get_user_model()

TOKEN = os.environ.get("TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Please send me your email to receive notifications."
    )


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    chat_id = update.message.chat_id
    logger.info(f"Received email: {email} with chat_id: {chat_id}")

    user = await sync_to_async(User.objects.filter(email=email).first)()
    if user:
        user.telegram_chat_id = chat_id
        await sync_to_async(user.save)()
        logger.info(f"Saved chat_id {chat_id} for user {email}")
        await update.message.reply_text(
            "Thank you! Your chat ID has been saved."
        )
    else:
        logger.error(f"User with email {email} not found")
        await update.message.reply_text("Sorry, I couldn't find that email.")


def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)
    )

    application.run_polling()


if __name__ == "__main__":
    run_bot()
