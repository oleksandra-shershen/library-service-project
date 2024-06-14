import logging
import os

import django
from django.contrib.auth import get_user_model
from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler

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
    await update.message.reply_text("Hello! Please send me your email to receive notifications.")


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    chat_id = update.message.chat_id
    user=User.objects.filter(email=email).first()
    if user:
        user.telegram_chat_id = chat_id
        user.save()
        await update.message.reply_text("Thank you! Your chat ID has been saved.")
    else:
        await update.message.reply_text("Sorry, I couldn't find that email.")


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("notify_new_book", get_email))

    application.run_polling()
