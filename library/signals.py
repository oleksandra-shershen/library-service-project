import os
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book

TELEGRAM_BOT_TOKEN = os.environ.get("TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

TELEGRAM_API_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
)


@receiver(post_save, sender=Book)
def send_telegram_notification(sender, instance, created, **kwargs):
    if created:
        message = f"New book added: {instance.title} by {instance.author}. Price: ${instance.daily_fee}"
        print(
            f"Sending message to {TELEGRAM_CHAT_ID}: {message}"
        )
        response = requests.post(
            TELEGRAM_API_URL,
            data={"chat_id": TELEGRAM_CHAT_ID, "text": message},
        )
        print(response.json())
