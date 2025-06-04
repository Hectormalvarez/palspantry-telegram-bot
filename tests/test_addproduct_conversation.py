import pytest
from unittest.mock import call
from telegram import (
    InlineKeyboardMarkup,
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
async def test_received_product_price_valid_asks_for_quantity(  # Renamed
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """
    Test that after receiving a valid product price, the bot asks for quantity
    and transitions to the PRODUCT_QUANTITY state, and user_data is preserved.
    """
    # Setup: Simulate that name and description are already in user_data
    mock_telegram_context.user_data = {
        "new_product": {"name": "Test Widget", "description": "A cool gadget."}
    }
    price_str = "25.50"
    expected_price_float = 25.50
    mock_update_message.message.text = price_str
    mock_update_message.effective_user = mocker.MagicMock(
        spec=User, id=12345
    )  # Owner ID

    # Action: Call the handler
    next_state = await bot_main.received_product_price(
        mock_update_message, mock_telegram_context
    )

    # Assert: New expected behavior
    assert (
        next_state == bot_main.PRODUCT_QUANTITY
    ), "Should transition to PRODUCT_QUANTITY"

    assert (
        "new_product" in mock_telegram_context.user_data
    ), "new_product data should be preserved"
    assert (
        mock_telegram_context.user_data["new_product"].get("price")
        == expected_price_float
    ), "Price should be stored"

    mock_update_message.message.reply_text.assert_called_once_with(
        f"Price set to {expected_price_float:.2f}.\n\n"
        "Now, how many units of this product are available? Please enter a whole number (e.g., 10)."  # New prompt
    )


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


@pytest.mark.asyncio
async def test_received_product_quantity_valid(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """Test receiving a valid product quantity."""
    # Setup: Simulate that name, description, and price are already in user_data
    mock_telegram_context.user_data = {
        "new_product": {
            "name": "Test Widget",
            "description": "Test Desc",
            "price": 19.99,
        }
    }
    quantity_str = "25"
    expected_quantity_int = 25
    mock_update_message.message.text = quantity_str
    # Add effective_user for logging or other context needs if your handler uses it
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=12345)

    # Action: This function bot_main.received_product_quantity doesn't fully exist or is a stub,
    # so this test (or parts of it) will fail.
    next_state = await bot_main.received_product_quantity(
        mock_update_message, mock_telegram_context
    )

    # Assert: Expected behavior for the *final* version of received_product_quantity
    assert next_state == bot_main.PRODUCT_CATEGORY
    assert (
        mock_telegram_context.user_data["new_product"]["quantity"]
        == expected_quantity_int
    )
    mock_update_message.message.reply_text.assert_called_once_with(
        f"Quantity set to {expected_quantity_int}.\n\n"
        "Next, please specify a category for this product."
    )
    assert (
        "quantity" in mock_telegram_context.user_data["new_product"]
    )  # Ensure quantity was stored
    assert (
        "price" in mock_telegram_context.user_data["new_product"]
    )  # Ensure previous data is preserved


@pytest.mark.parametrize(
    "invalid_quantity_input, case_description",
    [
        ("abc", "non-integer string"),
        ("10.5", "float string"),
        ("0", "zero value"),
        ("-5", "negative value"),
        ("", "empty string"),
        ("   ", "whitespace only"),
    ],
)
@pytest.mark.asyncio
async def test_received_product_quantity_invalid_inputs(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    invalid_quantity_input: str,
    case_description: str,  # For pytest output clarity
):
    """Test receiving various invalid product quantities."""
    mock_telegram_context.user_data = {
        "new_product": {
            "name": "Test Widget",
            "description": "Test Desc",
            "price": 19.99,
        }
    }
    mock_update_message.message.text = invalid_quantity_input
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=12345)

    next_state = await bot_main.received_product_quantity(
        mock_update_message, mock_telegram_context
    )

    assert (
        next_state == bot_main.PRODUCT_QUANTITY
    )  # Should stay in the same state to re-prompt
    mock_update_message.message.reply_text.assert_called_once_with(
        "That doesn't look like a valid quantity. "
        "Please enter a whole positive number (e.g., 10), or type /cancel."
    )
    # Ensure quantity was not added or was not incorrectly processed
    assert "quantity" not in mock_telegram_context.user_data.get("new_product", {})


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
    args, kwargs = call_args_list[0]  # Get args and kwargs of the first (and only) call

    assert args[0] == "Product addition cancelled."
    assert isinstance(kwargs.get("reply_markup"), ReplyKeyboardRemove)
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
    assert isinstance(kwargs.get("reply_markup"), ReplyKeyboardRemove)
    assert "new_product" not in mock_telegram_context.user_data




@pytest.mark.parametrize(
    "invalid_category_input, case_description",
    [("", "empty string"), ("   ", "whitespace only")],
)
@pytest.mark.asyncio
async def test_received_product_category_invalid_empty_text_input(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    invalid_category_input: str,
    case_description: str,
):
    """Test receiving an empty or whitespace-only category name as text."""
    mock_telegram_context.user_data = {
        "new_product": {
            "name": "Test Widget",
            "description": "Test Desc",
            "price": 19.99,
            "quantity": 10,
        }
    }
    mock_update_message.message.text = invalid_category_input
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=12345)

    next_state = await bot_main.received_product_category(
        mock_update_message, mock_telegram_context
    )

    assert (
        next_state == bot_main.PRODUCT_CATEGORY
    )  # Should stay in the same state to re-prompt
    mock_update_message.message.reply_text.assert_called_once_with(
        "Category name cannot be empty. Please enter a category, or type /cancel."
    )
    assert "category" not in mock_telegram_context.user_data.get("new_product", {})
