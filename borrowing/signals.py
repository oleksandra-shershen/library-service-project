import os
import requests
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task
from borrowing.models import Borrowing
from user.models import User
from payment.models import Payment

TELEGRAM_BOT_TOKEN = os.environ.get("TOKEN")
TELEGRAM_API_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
)

FINE_MULTIPLIER = 2


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
        f"📚 New Borrowing Created!\n\n"
        f"📝 Borrowing Details:\n"
        f"   • Book: {instance.book.title}\n"
        f"   • Author: {instance.book.author}\n"
        f"   • Due Date: "
        f"{instance.expected_return_date.strftime('%d %B %Y')}\n"
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


@receiver(post_save, sender=Payment)
def handle_successful_payment(sender, instance, **kwargs):
    if instance.status == "PAID":
        borrowing = instance.borrowing
        user = borrowing.user
        message = (
            f"📚 Payment Successful!\n\n"
            f"📝 Borrowing Details:\n"
            f"   • Book: {borrowing.book.title}\n"
            f"   • Author: {borrowing.book.author}\n"
            f"   • Borrowed On: {borrowing.borrow_date.strftime('%d %B %Y')}\n"
            f"   • Due Date: "
            f"{borrowing.expected_return_date.strftime('%d %B %Y')}\n\n"
            f"💵 Payment Details:\n"
            f"   • Amount Paid: ${instance.money_to_pay / 100:.2f}\n"
            f"   • Payment Type: {instance.get_payment_type_display()}\n\n"
            f"Thank you for using our library services!"
        )
        if user.telegram_chat_id:
            async_task(send_telegram_message, user.telegram_chat_id, message)


def check_all_borrowings():
    borrowings = Borrowing.objects.all()
    borrowings_message = "📚 All Borrowings:\n\n"
    if borrowings.exists():
        for borrowing in borrowings:
            borrowings_message += (
                f"   • User: {borrowing.user.email}\n"
                f"   • Book: {borrowing.book.title}\n"
                f"   • Due Date: "
                f"{borrowing.expected_return_date.strftime('%d %B %Y')}\n\n"
            )
    else:
        borrowings_message += "No borrowings found in the database."
    return borrowings_message


def check_overdue_borrowings():
    today = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today, actual_return_date__isnull=True
    )
    overdue_message = "⏰ Overdue Borrowings:\n\n"
    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            user = borrowing.user
            message = (
                f"⚠️ Reminder: Your borrowing is overdue!\n\n"
                f"   • Book: {borrowing.book.title}\n"
                f"   • Author: {borrowing.book.author}\n"
                f"   • Due Date: "
                f"{borrowing.expected_return_date.strftime('%d %B %Y')}\n"
            )
            if user.telegram_chat_id:
                async_task(
                    send_telegram_message, user.telegram_chat_id, message
                )
                overdue_message += message + "\n"
    else:
        overdue_message += "✅ No borrowings overdue today!"
        users = User.objects.exclude(telegram_chat_id__isnull=True)
        for user in users:
            if user.telegram_chat_id:
                async_task(
                    send_telegram_message,
                    user.telegram_chat_id,
                    overdue_message,
                )
    return overdue_message


@receiver(post_save, sender=Borrowing)
def handle_return_borrowing(sender, instance, **kwargs):
    if (
        instance.actual_return_date
        and instance.actual_return_date > instance.expected_return_date
    ):
        overdue_days = (
            instance.actual_return_date - instance.expected_return_date
        ).days
        fine_amount = overdue_days * instance.book.daily_fee * FINE_MULTIPLIER

        if instance.user.telegram_chat_id:
            fine_message = (
                f"⚠️ Your borrowing is overdue!\n\n"
                f"📝 Borrowing Details:\n"
                f"   • Book: {instance.book.title}\n"
                f"   • Author: {instance.book.author}\n"
                f"   • Due Date: "
                f"{instance.expected_return_date.strftime('%d %B %Y')}\n"
                f"   • Actual Return Date: "
                f"{instance.actual_return_date.strftime('%d %B %Y')}\n\n"
                f"💵 Fine Details:\n"
                f"   • Amount Due: ${fine_amount / 100:.2f}\n"
                f"Please complete the payment to avoid further penalties."
            )
            async_task(
                send_telegram_message,
                instance.user.telegram_chat_id,
                fine_message,
            )


def get_user_upcoming_borrowings(user):
    today = timezone.now().date()
    upcoming_message = "📚 Upcoming Borrowings:\n\n"
    nearest_borrowing = (
        Borrowing.objects.filter(user=user, expected_return_date__gte=today)
        .order_by("expected_return_date")
        .first()
    )
    if nearest_borrowing:
        upcoming_message += (
            f"🔔 Upcoming Borrowing Reminder:\n"
            f"   • Book: {nearest_borrowing.book.title}\n"
            f"   • Author: {nearest_borrowing.book.author}\n"
            f"   • Due Date: "
            f"{nearest_borrowing.expected_return_date.strftime('%d %B %Y')}\n"
        )
    else:
        upcoming_message += "✅ No upcoming borrowings found."
    return upcoming_message


def notify_users_about_upcoming_borrowing():
    users = User.objects.exclude(telegram_chat_id__isnull=True)
    for user in users:
        upcoming_message = get_user_upcoming_borrowings(user)
        if user.telegram_chat_id:
            async_task(
                send_telegram_message, user.telegram_chat_id, upcoming_message
            )
