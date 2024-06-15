import os
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from library.models import Book
from user.models import User

TELEGRAM_BOT_TOKEN = os.environ.get("TOKEN")
TELEGRAM_API_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
)


def send_telegram_message(chat_id, message):
    response = requests.post(
        TELEGRAM_API_URL,
        data={"chat_id": chat_id, "text": message},
    )
    print(response.json())


@receiver(post_save, sender=Book)
def send_telegram_notification(sender, instance, created, **kwargs):
    if created:
        users = User.objects.exclude(telegram_chat_id__isnull=True)
        message = (
            f"New book added: {instance.title} by {instance.author}.\n"
            f"Price: ${instance.daily_fee}"
        )
        for user in users:
            chat_id = user.telegram_chat_id
            if chat_id:
                response = requests.post(
                    TELEGRAM_API_URL,
                    data={"chat_id": chat_id, "text": message},
                )
                print(response.json())
