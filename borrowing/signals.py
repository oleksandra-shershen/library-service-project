import os
import requests
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task
from borrowing.models import Borrowing
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


def send_borrowing_notification(instance_id):
    instance = Borrowing.objects.get(id=instance_id)
    user = instance.user
    message = (
        f"New borrowing created:\n"
        f"Book: {instance.book.title}\n"
        f"Author: {instance.book.author}\n"
        f"Due date: {instance.expected_return_date}\n"
    )
    if user.telegram_chat_id:
        response = requests.post(
            TELEGRAM_API_URL,
            data={"chat_id": user.telegram_chat_id, "text": message},
        )
        print(response.json())


@receiver(post_save, sender=Borrowing)
def handle_new_borrowing(sender, instance, created, **kwargs):
    if created:
        async_task(send_borrowing_notification, instance.id)


def check_all_borrowings():
    borrowings = Borrowing.objects.all()
    admin_users = User.objects.filter(is_staff=True)
    borrowings_message = "All borrowings:\n"
    if borrowings.exists():
        for borrowing in borrowings:
            borrowings_message += (
                f"User: {borrowing.user.email}, "
                f"Book: {borrowing.book.title}, "
                f"Due date: {borrowing.expected_return_date}\n"
            )
    else:
        borrowings_message += "No borrowings found in the database."

    for admin in admin_users:
        if admin.telegram_chat_id:
            async_task(
                send_telegram_message,
                admin.telegram_chat_id,
                borrowings_message,
            )


def check_overdue_borrowings():
    today = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today, actual_return_date__isnull=True
    )
    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            user = borrowing.user
            message = (
                f"Reminder: Your borrowing is overdue!\n"
                f"Book: {borrowing.book.title}\n"
                f"Author: {borrowing.book.author}\n"
                f"Due date: {borrowing.expected_return_date}\n"
            )
            if user.telegram_chat_id:
                async_task(
                    send_telegram_message, user.telegram_chat_id, message
                )
    else:
        users = User.objects.exclude(telegram_chat_id__isnull=True)
        for user in users:
            if user.telegram_chat_id:
                async_task(
                    send_telegram_message,
                    user.telegram_chat_id,
                    "No borrowings overdue today!",
                )


def notify_users_about_upcoming_borrowing():
    users = User.objects.exclude(telegram_chat_id__isnull=True)
    today = timezone.now().date()
    for user in users:
        nearest_borrowing = (
            Borrowing.objects.filter(
                user=user, expected_return_date__gte=today
            )
            .order_by("expected_return_date")
            .first()
        )

        if nearest_borrowing:
            message = (
                f"Upcoming borrowing reminder:\n"
                f"Book: {nearest_borrowing.book.title}\n"
                f"Author: {nearest_borrowing.book.author}\n"
                f"Due date: {nearest_borrowing.expected_return_date}\n"
            )
            async_task(send_telegram_message, user.telegram_chat_id, message)
