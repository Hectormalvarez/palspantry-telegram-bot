import pytest
from telegram import (
    ReplyKeyboardRemove,
    Update,
    User,
)  # For type hinting and spec for MagicMock
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
)  # For ConversationHandler.END and type hints

import bot_main  # To access your state constants and handler functions
from persistence.abstract_persistence import (
    AbstractPantryPersistence,
)  # For type hinting


PRODUCT_NAME = 0
PRODUCT_DESCRIPTION = 1
PRODUCT_PRICE = 2


# --- Tests for add_product_start ---
@pytest.mark.asyncio
async def test_add_product_start_as_owner(
    mocker,  # pytest-mock's mocker fixture
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,  # Using the type from telegram.ext
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test /addproduct start when user is the owner."""
    test_owner_id = 12345
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=test_owner_id)

    # Configure persistence mock for owner check
    mock_persistence_layer.get_bot_owner.return_value = test_owner_id

    # Ensure user_data is initially empty or does not contain 'new_product'
    mock_telegram_context.user_data = {}

    next_state = await bot_main.add_product_start(
        mock_update_message, mock_telegram_context
    )

    assert next_state == bot_main.PRODUCT_NAME
    mock_update_message.message.reply_text.assert_called_once_with(
        "Let's add a new product! First, what is the product's name?"
    )
    assert "new_product" in mock_telegram_context.user_data
    assert mock_telegram_context.user_data["new_product"] == {}


@pytest.mark.asyncio
async def test_add_product_start_as_non_owner(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test /addproduct start when user is not the owner."""
    actual_owner_id = 12345
    non_owner_id = 67890
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=non_owner_id)

    mock_persistence_layer.get_bot_owner.return_value = actual_owner_id
    mock_telegram_context.user_data = {}  # Ensure clean user_data

    next_state = await bot_main.add_product_start(
        mock_update_message, mock_telegram_context
    )

    assert next_state == ConversationHandler.END
    mock_update_message.message.reply_text.assert_called_once_with(
        "Sorry, this command is only for the bot owner."
    )
    assert "new_product" not in mock_telegram_context.user_data


# --- Tests for received_product_name ---
@pytest.mark.asyncio
async def test_received_product_name_valid(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """Test receiving a valid product name."""
    mock_telegram_context.user_data = {
        "new_product": {}
    }  # Simulate state after add_product_start
    product_name = "Super Widget"
    mock_update_message.message.text = product_name
    mock_update_message.effective_user = mocker.MagicMock(
        spec=User, id=123
    )  # Add for logger

    next_state = await bot_main.received_product_name(
        mock_update_message, mock_telegram_context
    )

    assert next_state == bot_main.PRODUCT_DESCRIPTION
    assert mock_telegram_context.user_data["new_product"]["name"] == product_name
    mock_update_message.message.reply_text.assert_called_once_with(
        f"Great! Product name is '{product_name}'.\n\n"
        "Now, please enter a description for the product."
    )


@pytest.mark.asyncio
async def test_received_product_name_invalid_empty(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """Test receiving an empty product name."""
    mock_telegram_context.user_data = {"new_product": {}}
    mock_update_message.message.text = "   "  # Empty/whitespace
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=123)

    next_state = await bot_main.received_product_name(
        mock_update_message, mock_telegram_context
    )

    assert next_state == bot_main.PRODUCT_NAME
    mock_update_message.message.reply_text.assert_called_once_with(
        "Product name cannot be empty. Please enter a name, or type /cancel to exit."
    )
    assert "name" not in mock_telegram_context.user_data["new_product"]


# --- Tests for received_product_description ---
@pytest.mark.asyncio
async def test_received_product_description_valid(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """Test receiving a valid product description."""
    product_name = "Super Widget"
    mock_telegram_context.user_data = {
        "new_product": {"name": product_name}
    }  # Simulate previous state
    description = "The best widget ever."
    mock_update_message.message.text = description
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=123)

    next_state = await bot_main.received_product_description(
        mock_update_message, mock_telegram_context
    )

    assert next_state == bot_main.PRODUCT_PRICE
    assert mock_telegram_context.user_data["new_product"]["description"] == description
    mock_update_message.message.reply_text.assert_called_once_with(
        f"Description noted.\n\n"
        "Now, what's the price for this product? Please enter a number (e.g., 10.99 or 5)."
    )


@pytest.mark.asyncio
async def test_received_product_description_invalid_empty(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """Test receiving an empty product description."""
    mock_telegram_context.user_data = {"new_product": {"name": "Test Widget"}}
    mock_update_message.message.text = ""  # Empty
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=123)

    next_state = await bot_main.received_product_description(
        mock_update_message, mock_telegram_context
    )

    assert next_state == bot_main.PRODUCT_DESCRIPTION
    mock_update_message.message.reply_text.assert_called_once_with(
        "Product description cannot be empty. Please enter a description, or type /cancel to exit."
    )
    assert "description" not in mock_telegram_context.user_data["new_product"]


# --- Tests for received_product_price ---
@pytest.mark.asyncio
async def test_received_product_price_valid(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """Test receiving a valid product price."""
    mock_telegram_context.user_data = {
        "new_product": {"name": "Test Widget", "description": "Test Desc"}
    }
    price_str = "19.99"
    expected_price_float = 19.99
    mock_update_message.message.text = price_str
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=123)

    next_state = await bot_main.received_product_price(
        mock_update_message, mock_telegram_context
    )

    assert next_state == ConversationHandler.END  # Current implementation ends here
    # Price was stored, then new_product was deleted.
    # We check the reply_text to confirm price was processed.
    mock_update_message.message.reply_text.assert_called_once_with(
        f"Price set to {expected_price_float:.2f}.\n\n"
        "Next, we'll ask for the quantity. (Quantity step not implemented yet)."
    )
    # Assert that new_product was cleaned up from user_data as per current handler logic
    assert "new_product" not in mock_telegram_context.user_data


@pytest.mark.asyncio
async def test_received_product_price_invalid_non_numeric(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """Test receiving a non-numeric price."""
    mock_telegram_context.user_data = {
        "new_product": {"name": "Test Widget", "description": "Test Desc"}
    }
    mock_update_message.message.text = "abc"
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=123)

    next_state = await bot_main.received_product_price(
        mock_update_message, mock_telegram_context
    )

    assert next_state == bot_main.PRODUCT_PRICE
    mock_update_message.message.reply_text.assert_called_once_with(
        "That doesn't look like a valid price. "
        "Please enter a positive number (e.g., 10.99 or 5), or type /cancel."
    )
    assert "price" not in mock_telegram_context.user_data["new_product"]


@pytest.mark.asyncio
async def test_received_product_price_invalid_zero_or_negative(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """Test receiving a zero or negative price."""
    mock_telegram_context.user_data = {
        "new_product": {"name": "Test Widget", "description": "Test Desc"}
    }
    mock_update_message.message.text = "-5"
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=123)

    next_state = await bot_main.received_product_price(
        mock_update_message, mock_telegram_context
    )

    assert next_state == bot_main.PRODUCT_PRICE
    mock_update_message.message.reply_text.assert_called_once_with(
        "That doesn't look like a valid price. "
        "Please enter a positive number (e.g., 10.99 or 5), or type /cancel."
    )
    assert "price" not in mock_telegram_context.user_data["new_product"]


# --- Tests for cancel_add_product ---
@pytest.mark.asyncio
async def test_cancel_add_product_with_data(
    mock_update_message: Update, mock_telegram_context: ContextTypes.DEFAULT_TYPE
):
    """Test cancelling the conversation when some data exists."""
    mock_telegram_context.user_data = {"new_product": {"name": "Test"}}

    next_state = await bot_main.cancel_add_product(
        mock_update_message, mock_telegram_context
    )

    assert next_state == ConversationHandler.END
    mock_update_message.message.reply_text.assert_called_once()
    call_args_list = mock_update_message.message.reply_text.call_args_list
    args, kwargs = call_args_list[0] # Get args and kwargs of the first (and only) call

    assert args[0] == "Product addition cancelled."
    assert isinstance(kwargs.get('reply_markup'), ReplyKeyboardRemove)
    assert "new_product" not in mock_telegram_context.user_data


@pytest.mark.asyncio
async def test_cancel_add_product_without_data(
    mock_update_message: Update, mock_telegram_context: ContextTypes.DEFAULT_TYPE
):
    """Test cancelling the conversation when no new_product data exists."""
    mock_telegram_context.user_data = {}  # Ensure no 'new_product' key

    next_state = await bot_main.cancel_add_product(
        mock_update_message, mock_telegram_context
    )

    assert next_state == ConversationHandler.END
    mock_update_message.message.reply_text.assert_called_once()
    call_args_list = mock_update_message.message.reply_text.call_args_list
    args, kwargs = call_args_list[0]

    assert args[0] == "Product addition cancelled."
    assert isinstance(kwargs.get('reply_markup'), ReplyKeyboardRemove)
    assert "new_product" not in mock_telegram_context.user_data
