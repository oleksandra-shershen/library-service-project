import os
import requests
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task
from borrowing.models import Borrowing
from library.models import Book
from user.models import User
from payment.views import create_payment_session

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
    return borrowings_message


def check_overdue_borrowings():
    today = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today, actual_return_date__isnull=True
    )
    overdue_message = "Overdue borrowings:\n"
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
                overdue_message += message + "\n"
    else:
        overdue_message += "No borrowings overdue today!"
        users = User.objects.exclude(telegram_chat_id__isnull=True)
        for user in users:
            if user.telegram_chat_id:
                async_task(
                    send_telegram_message,
                    user.telegram_chat_id,
                    overdue_message,
                )
    return overdue_message


def get_user_upcoming_borrowings(user):
    today = timezone.now().date()
    upcoming_message = "Upcoming borrowings:\n"
    nearest_borrowing = (
        Borrowing.objects.filter(user=user, expected_return_date__gte=today)
        .order_by("expected_return_date")
        .first()
    )
    if nearest_borrowing:
        upcoming_message += (
            f"Upcoming borrowing reminder:\n"
            f"Book: {nearest_borrowing.book.title}\n"
            f"Author: {nearest_borrowing.book.author}\n"
            f"Due date: {nearest_borrowing.expected_return_date}\n"
        )
    else:
        upcoming_message += "No upcoming borrowings found."
    return upcoming_message


def notify_users_about_upcoming_borrowing():
    users = User.objects.exclude(telegram_chat_id__isnull=True)
    for user in users:
        upcoming_message = get_user_upcoming_borrowings(user)
        if user.telegram_chat_id:
            async_task(
                send_telegram_message, user.telegram_chat_id, upcoming_message
            )

