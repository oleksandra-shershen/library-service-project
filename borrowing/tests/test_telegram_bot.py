import pytest
from unittest.mock import AsyncMock, patch
from telegram import Update, User as TGUser, Message
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
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
