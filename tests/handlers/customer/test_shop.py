import pytest
from unittest.mock import ANY

from telegram import Update, User, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from handlers.customer import shop
from persistence.abstract_persistence import AbstractPantryPersistence


@pytest.mark.asyncio
async def test_shop_start_with_categories(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test /shop command when categories exist."""
    # Arrange
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=98765)
    mock_update_message.callback_query = None  # Ensure it's treated as a command
    mock_categories = ["Bakery", "Drinks"]
    mock_telegram_context.bot.send_message = mocker.AsyncMock()
    mock_persistence_layer.get_all_categories.return_value = mock_categories

    # Act
    await shop.shop_start(mock_update_message, mock_telegram_context)

    # Assert
    mock_persistence_layer.get_all_categories.assert_called_once()
    # Check that the call included a keyboard
    call_args = mock_telegram_context.bot.send_message.call_args
    assert call_args.kwargs["text"] == "Welcome to PalsPantry! Select a category:"
    sent_markup = call_args.kwargs["reply_markup"]
    assert isinstance(sent_markup, InlineKeyboardMarkup)
    assert len(sent_markup.inline_keyboard) == 3
    assert sent_markup.inline_keyboard[0][0].text == "Bakery"
    assert sent_markup.inline_keyboard[1][0].text == "Drinks"

    # Check the new close button row
    close_row = sent_markup.inline_keyboard[2]
    assert len(close_row) == 1
    assert close_row[0].text == "❌ Close"
    assert close_row[0].callback_data == "close_shop"


@pytest.mark.asyncio
async def test_shop_start_no_categories(
    mocker,
    mock_update_message: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test /shop command when the shop is empty."""
    # Arrange
    mock_update_message.effective_user = mocker.MagicMock(spec=User, id=98765)
    mock_update_message.callback_query = None  # Ensure it's treated as a command
    mock_persistence_layer.get_all_categories.return_value = []

    # Act
    await shop.shop_start(mock_update_message, mock_telegram_context)

    # Assert
    mock_persistence_layer.get_all_categories.assert_called_once()
    mock_update_message.message.reply_text.assert_called_once_with(
        "The shop is currently empty. Please check back later!"
    )


@pytest.mark.asyncio
async def test_handle_category_selection_with_products(
    mocker,
    mock_update_callback_query: Update,  # Uses our new fixture
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test category button click when products are found."""
    # Arrange
    category_name = "Bakery"
    mock_update_callback_query.callback_query.data = f"category_{category_name}"

    # Mock the context.matches to simulate regex capture
    mock_match = mocker.MagicMock()
    mock_match.group.return_value = category_name
    mock_telegram_context.matches = [mock_match]

    # Add IDs to our mock products
    mock_products = [
        {"id": "prod_123", "name": "Croissant", "price": 2.50},
        {"id": "prod_456", "name": "Baguette", "price": 3.00},
    ]
    mock_persistence_layer.get_products_by_category.return_value = mock_products

    # Act
    await shop.handle_category_selection(
        mock_update_callback_query, mock_telegram_context
    )

    # Assert
    mock_update_callback_query.callback_query.answer.assert_called_once()
    mock_persistence_layer.get_products_by_category.assert_called_once_with(
        category_name
    )

    # Assert that the bot replies with buttons
    mock_update_callback_query.callback_query.edit_message_text.assert_called_once_with(
        text=f"<b>{category_name}</b>",
        reply_markup=ANY,
        parse_mode=ParseMode.HTML,
    )
    sent_markup = mock_update_callback_query.callback_query.edit_message_text.call_args.kwargs.get(
        "reply_markup"
    )
    assert isinstance(sent_markup, InlineKeyboardMarkup)
    assert len(sent_markup.inline_keyboard) == 3
    # Check the first button
    assert sent_markup.inline_keyboard[0][0].text == "Croissant ($2.50)"
    assert sent_markup.inline_keyboard[0][0].callback_data == "product_prod_123"
    # Check the second button
    assert sent_markup.inline_keyboard[1][0].text == "Baguette ($3.00)"
    assert sent_markup.inline_keyboard[1][0].callback_data == "product_prod_456"
    # Check the navigation row
    nav_row = sent_markup.inline_keyboard[2]
    assert len(nav_row) == 2  # Expect two buttons in the navigation row
    assert nav_row[0].text == "<< Back to Categories"
    assert nav_row[0].callback_data == "navigate_to_categories"
    assert nav_row[1].text == "❌ Close"
    assert nav_row[1].callback_data == "close_shop"


@pytest.mark.asyncio
async def test_handle_category_selection_no_products(
    mocker,
    mock_update_callback_query: Update,  # Uses our new fixture
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test category button click when category is empty."""
    # Arrange
    category_name = "Empty Category"
    mock_update_callback_query.callback_query.data = f"category_{category_name}"

    mock_match = mocker.MagicMock()
    mock_match.group.return_value = category_name
    mock_telegram_context.matches = [mock_match]

    mock_persistence_layer.get_products_by_category.return_value = []

    # Act
    await shop.handle_category_selection(
        mock_update_callback_query, mock_telegram_context
    )

    # Assert
    mock_update_callback_query.callback_query.answer.assert_called_once()
    mock_persistence_layer.get_products_by_category.assert_called_once_with(
        category_name
    )

    expected_text = "No products here."
    mock_update_callback_query.callback_query.edit_message_text.assert_called_once_with(
        expected_text
    )


@pytest.mark.asyncio
async def test_handle_product_selection(
    mocker,
    mock_update_callback_query: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test product button click shows product details and 'Add to Cart' button."""
    # Arrange
    product_id = "prod_123"
    category_name = "Bakery"  # Needed for the "Back" button
    mock_update_callback_query.callback_query.data = f"product_{product_id}"

    # Mock the context.matches to simulate regex capture
    mock_match = mocker.MagicMock()
    mock_match.group.return_value = product_id
    mock_telegram_context.matches = [mock_match]

    mock_product = {
        "id": product_id,
        "name": "Croissant",
        "description": "A flaky, buttery pastry.",
        "price": 2.50,
        "category": category_name,
        "quantity": 10,  # <--- NEW LINE ADDED
    }
    mock_persistence_layer.get_product.return_value = mock_product

    # Act
    await shop.handle_product_selection(
        mock_update_callback_query, mock_telegram_context
    )

    # Assert
    mock_update_callback_query.callback_query.answer.assert_called_once()
    mock_persistence_layer.get_product.assert_called_once_with(product_id)

    expected_text = (
        f"<b>{mock_product['name']}</b>\n"
        f"<i>{mock_product.get('description', '')}</i>\n\n"
        f"Price: <b>${mock_product['price']:.2f}</b>\n"
        f"Stock: {mock_product['quantity']} available"
    )
    mock_update_callback_query.callback_query.edit_message_text.assert_called_once_with(
        text=expected_text,
        reply_markup=ANY,
        parse_mode=ParseMode.HTML,
    )

    # Check that the new keyboard is correct
    sent_markup = mock_update_callback_query.callback_query.edit_message_text.call_args.kwargs.get(
        "reply_markup"
    )
    assert isinstance(sent_markup, InlineKeyboardMarkup)
    assert len(sent_markup.inline_keyboard) == 2  # Expect Two row of buttons
    assert sent_markup.inline_keyboard[0][0].text == "🛒 Add to Cart"
    assert (
        sent_markup.inline_keyboard[0][0].callback_data == f"add_to_cart_{product_id}"
    )

    # Assert the navigation buttons are in the second row
    nav_row = sent_markup.inline_keyboard[1]
    assert len(nav_row) == 2
    assert nav_row[0].text == f"<< Back to {category_name}"
    assert nav_row[0].callback_data == f"navigate_to_products_{category_name}"
    assert nav_row[1].text == "❌ Close"
    assert nav_row[1].callback_data == "close_shop"


@pytest.mark.asyncio
async def test_handle_add_to_cart_new_item(
    mocker,
    mock_update_callback_query: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test 'Add to Cart' button for a new item."""
    # Arrange
    product_id = "prod_123"
    mock_update_callback_query.callback_query.data = f"add_to_cart_{product_id}"

    # Mock the context.matches to simulate regex capture
    mock_match = mocker.MagicMock()
    mock_match.group.return_value = product_id
    mock_telegram_context.matches = [mock_match]

    # Mock persistence to get the product name for the confirmation message
    mock_persistence_layer.get_product.return_value = {"name": "Croissant"}
    mock_persistence_layer.add_to_cart.return_value = 1

    # Act
    await shop.handle_add_to_cart(mock_update_callback_query, mock_telegram_context)

    # Assert
    mock_persistence_layer.add_to_cart.assert_called_once_with(user_id=98765, product_id=product_id, quantity=1)
    # Check that the user received a confirmation pop-up
    # Remove 'text=' keyword argument as the implementation uses positional args
    mock_update_callback_query.callback_query.answer.assert_called_once_with(
        "Croissant added to cart! (Total: 1)"
    )


@pytest.mark.asyncio
async def test_handle_add_to_cart_existing_item(
    mocker,
    mock_update_callback_query: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test 'Add to Cart' button for an item already in the cart."""
    # Arrange
    product_id = "prod_123"
    mock_update_callback_query.callback_query.data = f"add_to_cart_{product_id}"

    mock_match = mocker.MagicMock()
    mock_match.group.return_value = product_id
    mock_telegram_context.matches = [mock_match]

    mock_persistence_layer.get_product.return_value = {"name": "Croissant"}
    mock_persistence_layer.add_to_cart.return_value = 2

    # Act
    await shop.handle_add_to_cart(mock_update_callback_query, mock_telegram_context)

    # Assert
    mock_persistence_layer.add_to_cart.assert_called_once_with(user_id=98765, product_id=product_id, quantity=1)
    # Remove 'text=' keyword argument
    mock_update_callback_query.callback_query.answer.assert_called_once_with(
        "Croissant added to cart! (Total: 2)"
    )


@pytest.mark.asyncio
async def test_handle_close_shop(
    mock_update_callback_query: Update,
):
    """Test that the 'close_shop' callback ends the interaction"""
    # Arrange
    query = mock_update_callback_query.callback_query
    query.data = "close_shop"

    # Act
    await shop.handle_close_shop(mock_update_callback_query, None)

    # Assert
    query.answer.assert_called_once()
    query.edit_message_text.assert_called_once_with(
        "Shop closed. See you soon!",
        reply_markup=None,  # Asserts the keyboard is removed
    )


@pytest.mark.asyncio
async def test_handle_back_to_categories(
    mocker,
    mock_update_callback_query: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test 'Back to Categories' callback displays the category list."""
    # Arrange
    query = mock_update_callback_query.callback_query
    query.data = "navigate_to_categories"

    # Mock the persistence layer to return some categories
    mock_categories = ["Bakery", "Drinks"]
    mock_persistence_layer.get_all_categories.return_value = mock_categories

    # Act
    # This function doesn't exist yet, which will cause the test to fail.
    await shop.handle_back_to_categories(
        mock_update_callback_query, mock_telegram_context
    )

    # Assert
    query.answer.assert_called_once()
    mock_persistence_layer.get_all_categories.assert_called_once()

    # Assert that the message is edited to show the category list
    query.edit_message_text.assert_called_once_with(
        text="Welcome to PalsPantry! Select a category:",
        reply_markup=ANY,
    )

    # Verify the keyboard is correct
    sent_markup = query.edit_message_text.call_args.kwargs.get("reply_markup")
    assert isinstance(sent_markup, InlineKeyboardMarkup)
    assert len(sent_markup.inline_keyboard) == 3  # 2 categories, 1 close button
    assert sent_markup.inline_keyboard[0][0].text == "Bakery"
    assert sent_markup.inline_keyboard[0][0].callback_data == "category_Bakery"
    assert sent_markup.inline_keyboard[1][0].text == "Drinks"
    assert sent_markup.inline_keyboard[1][0].callback_data == "category_Drinks"
    close_row = sent_markup.inline_keyboard[2]
    assert len(close_row) == 1
    assert close_row[0].text == "❌ Close"
    assert close_row[0].callback_data == "close_shop"


@pytest.mark.asyncio
async def test_handle_back_to_products(
    mocker,
    mock_update_callback_query: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
    mock_persistence_layer: AbstractPantryPersistence,
):
    """Test 'Back to Products' callback re-uses category selection logic."""
    # Arrange
    query = mock_update_callback_query.callback_query
    category_name = "Bakery"
    # This callback will be handled by the same function as "category_Bakery"
    query.data = f"navigate_to_products_{category_name}"

    # We must simulate the regex match that the CallbackQueryHandler performs.
    # The handler will find `Bakery` and store it in `context.matches`.
    mock_match = mocker.MagicMock()
    mock_match.group.return_value = category_name
    mock_telegram_context.matches = [mock_match]

    # Mock the persistence layer to return products for this category
    mock_products = [
        {"id": "prod_123", "name": "Croissant", "price": 2.50},
    ]
    mock_persistence_layer.get_products_by_category.return_value = mock_products

    # Act
    # We call the *existing* function to confirm it works for this case.
    await shop.handle_category_selection(
        mock_update_callback_query, mock_telegram_context
    )

    # Assert
    query.answer.assert_called_once()
    mock_persistence_layer.get_products_by_category.assert_called_once_with(
        category_name
    )

    # Assert that the product list keyboard is regenerated correctly
    sent_markup = query.edit_message_text.call_args.kwargs.get("reply_markup")
    assert isinstance(sent_markup, InlineKeyboardMarkup)
    assert len(sent_markup.inline_keyboard) == 2  # 1 product, 1 nav row
    assert sent_markup.inline_keyboard[0][0].text == "Croissant ($2.50)"


@pytest.mark.asyncio
async def test_handle_close_shop(
    mock_update_callback_query: Update,
    mock_telegram_context: ContextTypes.DEFAULT_TYPE,
):
    """Test that the close_shop callback deletes the message."""
    # Arrange
    query = mock_update_callback_query.callback_query
    query.data = "close_shop"

    # Act
    await shop.handle_close_shop(mock_update_callback_query, mock_telegram_context)

    # Assert
    query.answer.assert_called_once()
    query.edit_message_text.assert_called_once_with(
        "Shop closed. See you soon!",
        reply_markup=None,  # Explicitly check that the keyboard is removed
    )
