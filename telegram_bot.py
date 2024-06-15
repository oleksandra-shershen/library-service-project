import logging
import os

import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")
django.setup()

from django.contrib.auth import get_user_model
from telegram.ext import (
    ContextTypes,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from telegram import Update
from asgiref.sync import sync_to_async
from borrowing.signals import (
    check_all_borrowings,
    check_overdue_borrowings,
    get_user_upcoming_borrowings,
)

User = get_user_model()

TOKEN = os.environ.get("TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

EMAIL, FIRST_NAME, LAST_NAME = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Please send me your email to receive notifications."
    )
    return EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text(
        "Thank you! Now, please send me your first name."
    )
    return FIRST_NAME


async def get_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["first_name"] = update.message.text
    await update.message.reply_text(
        "Great! Finally, please send me your last name."
    )
    return LAST_NAME


async def get_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_name"] = update.message.text
    email = context.user_data["email"]
    first_name = context.user_data["first_name"]
    last_name = context.user_data["last_name"]
    chat_id = update.message.chat_id

    logger.info(
        f"Received email: {email}, first name: {first_name}, last name: {last_name} with chat_id: {chat_id}"
    )

    user = await sync_to_async(
        User.objects.filter(
            email=email, first_name=first_name, last_name=last_name
        ).first
    )()
    if user:
        user.telegram_chat_id = chat_id
        await sync_to_async(user.save)()
        logger.info(f"Saved chat_id {chat_id} for user {email}")
        await update.message.reply_text(
            "Thank you! Your chat ID has been saved."
        )
    else:
        logger.error(
            f"User with email {email}, first name {first_name}, and last name {last_name} not found"
        )
        await update.message.reply_text("Sorry, I couldn't find that user.")

    return ConversationHandler.END


async def command_all_borrowings(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.message.chat_id
    user = await sync_to_async(
        User.objects.filter(telegram_chat_id=chat_id).first
    )()
    if user and user.is_staff:
        borrowings_message = await sync_to_async(check_all_borrowings)()
        await context.bot.send_message(
            chat_id=chat_id, text=borrowings_message
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id, text="Access denied. You are not an admin."
        )


async def command_overdue_borrowings(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.message.chat_id
    overdue_message = await sync_to_async(check_overdue_borrowings)()
    await context.bot.send_message(chat_id=chat_id, text=overdue_message)


async def command_upcoming_borrowings(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.message.chat_id
    user = await sync_to_async(
        User.objects.filter(telegram_chat_id=chat_id).first
    )()
    if user:
        upcoming_message = await sync_to_async(get_user_upcoming_borrowings)(
            user
        )
        await context.bot.send_message(chat_id=chat_id, text=upcoming_message)
    else:
        await context.bot.send_message(
            chat_id=chat_id, text="User not found. Please register first."
        )


def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)
            ],
            FIRST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_first_name)
            ],
            LAST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_last_name)
            ],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(
        CommandHandler("all_borrow", command_all_borrowings)
    )
    application.add_handler(
        CommandHandler("overdue_borrow", command_overdue_borrowings)
    )
    application.add_handler(
        CommandHandler("upcoming_borrow", command_upcoming_borrowings)
    )

    application.run_polling()


if __name__ == "__main__":
    run_bot()
