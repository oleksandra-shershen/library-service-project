import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from django.utils import timezone
from telegram import Update, Message
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")

import django

django.setup()

from borrowing.models import Borrowing
from borrowing.signals import check_overdue_borrowings
from telegram_bot import (
    start,
    get_email,
    get_first_name,
    get_last_name,
    command_all_borrowings,
    command_upcoming_borrowings,
)

User = get_user_model()


@pytest.fixture
def mock_update():
    return AsyncMock(Update)


@pytest.fixture
def mock_context():
    context = AsyncMock(ContextTypes.DEFAULT_TYPE)
    context.bot.send_message = AsyncMock()
    return context


@pytest.mark.asyncio
@patch("telegram_bot.User.objects.filter")
async def test_start(mock_user_filter, mock_update, mock_context):
    mock_update.message = AsyncMock(Message)
    mock_update.message.chat_id = 12345
    mock_update.message.text = "test@example.com"
    mock_user_filter.return_value.first.return_value = None

    await start(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_with(
        "Hello! Please send me your email."
    )


@pytest.mark.asyncio
@patch("telegram_bot.User.objects.filter")
async def test_get_email(mock_user_filter, mock_update, mock_context):
    mock_update.message = AsyncMock(Message)
    mock_update.message.text = "test@example.com"
    mock_update.message.chat_id = 12345
    mock_user_filter.return_value.first.return_value = None

    await get_email(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_with(
        "Now, please send your first name."
    )


@pytest.mark.asyncio
@patch("telegram_bot.User.objects.filter")
async def test_get_first_name(mock_user_filter, mock_update, mock_context):
    mock_update.message = AsyncMock(Message)
    mock_update.message.text = "John"
    mock_update.message.chat_id = 12345
    mock_user_filter.return_value.first.return_value = None

    await get_first_name(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_with(
        "Now, please send your last name."
    )


@pytest.mark.asyncio
@patch("telegram_bot.User.objects.filter")
async def test_get_last_name(mock_user_filter, mock_update, mock_context):
    mock_update.message = AsyncMock(Message)
    mock_update.message.text = "Doe"
    mock_update.message.chat_id = 12345
    mock_user_filter.return_value.first.return_value = None

    await get_last_name(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_with(
        "Sorry, I couldn't find that email."
    )


@pytest.mark.asyncio
@patch("telegram_bot.check_all_borrowings")
@patch("telegram_bot.User.objects.filter")
async def test_command_all_borrowings(
    mock_user_filter, mock_check_all_borrowings, mock_update, mock_context
):
    mock_update.message = AsyncMock(Message)
    mock_update.message.chat_id = 12345
    mock_user_filter.return_value.first.return_value = await sync_to_async(
        User
    )(email="admin@example.com", is_staff=True, telegram_chat_id=12345)
    mock_check_all_borrowings.return_value = "All borrowings message"

    await command_all_borrowings(mock_update, mock_context)
    mock_context.bot.send_message.assert_called_with(
        chat_id=12345, text="All borrowings message"
    )


@pytest.mark.asyncio
@patch("telegram_bot.get_user_upcoming_borrowings")
@patch("telegram_bot.User.objects.filter")
async def test_command_upcoming_borrowings(
    mock_user_filter,
    mock_get_user_upcoming_borrowings,
    mock_update,
    mock_context,
):
    mock_update.message = AsyncMock(Message)
    mock_update.message.chat_id = 12345
    mock_user_filter.return_value.first.return_value = await sync_to_async(
        User
    )(email="user@example.com", is_staff=False, telegram_chat_id=12345)
    mock_get_user_upcoming_borrowings.return_value = (
        "Upcoming borrowings message"
    )

    await command_upcoming_borrowings(mock_update, mock_context)
    mock_context.bot.send_message.assert_called_with(
        chat_id=12345, text="Upcoming borrowings message"
    )


@pytest.mark.asyncio
@patch("borrowing.signals.timezone")
@patch("borrowing.signals.Borrowing.objects.filter")
@patch("borrowing.signals.async_task", new_callable=AsyncMock)
@patch("borrowing.signals.send_telegram_message", new_callable=AsyncMock)
@patch("borrowing.signals.User.objects.exclude")
async def test_check_overdue_borrowings(
    mock_user_exclude,
    mock_send_telegram_message,
    mock_async_task,
    mock_borrowing_filter,
    mock_timezone,
):
    today = timezone.now().date()
    mock_timezone.now.return_value.date.return_value = today

    mock_borrowing_1 = MagicMock()
    mock_borrowing_1.book.title = "Book 1"
    mock_borrowing_1.book.author = "Author 1"
    mock_borrowing_1.expected_return_date = today
    mock_borrowing_1.actual_return_date = None
    mock_user_1 = MagicMock()
    mock_user_1.email = "user1@example.com"
    mock_user_1.telegram_chat_id = "chat_id_1"
    mock_borrowing_1.user = mock_user_1

    mock_borrowing_2 = MagicMock()
    mock_borrowing_2.book.title = "Book 2"
    mock_borrowing_2.book.author = "Author 2"
    mock_borrowing_2.expected_return_date = today
    mock_borrowing_2.actual_return_date = None
    mock_user_2 = MagicMock()
    mock_user_2.email = "user2@example.com"
    mock_user_2.telegram_chat_id = "chat_id_2"
    mock_borrowing_2.user = mock_user_2

    mock_borrowing_queryset = MagicMock()
    mock_borrowing_queryset.exists.return_value = True
    mock_borrowing_queryset.__iter__.return_value = iter(
        [mock_borrowing_1, mock_borrowing_2]
    )
    mock_borrowing_filter.return_value = mock_borrowing_queryset

    await sync_to_async(check_overdue_borrowings)()

    expected_message_1 = (
        "⚠️ Reminder: Your borrowing is overdue!\n\n"
        "   • Book: Book 1\n"
        "   • Author: Author 1\n"
        "   • Due Date: {}\n".format(today.strftime("%d %B %Y"))
    )
    expected_message_2 = (
        "⚠️ Reminder: Your borrowing is overdue!\n\n"
        "   • Book: Book 2\n"
        "   • Author: Author 2\n"
        "   • Due Date: {}\n".format(today.strftime("%d %B %Y"))
    )

    print(mock_async_task.call_args_list)

    mock_async_task.assert_any_call(
        mock_send_telegram_message, "chat_id_1", expected_message_1
    )
    mock_async_task.assert_any_call(
        mock_send_telegram_message, "chat_id_2", expected_message_2
    )
