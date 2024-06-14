import logging
import os

from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler

TOKEN = os.environ.get("TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Siemano!")


async def notify_new_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    book_title = context.args[0] if context.args else "Unknown"
    author = context.args[1] if context.args > 1 else "Unknown"
    price = context.args[2] if context.args > 2 else "Unknown"
    await update.message.reply_text(
        f"New book added: {book_title} by {author}. Price: ${price}"
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("notify_new_book", notify_new_book))

    application.run_polling()
