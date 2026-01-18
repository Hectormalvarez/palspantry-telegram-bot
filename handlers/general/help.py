from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on available commands."""
    text = """
<b>Available commands:</b>

🛒 <b>Shopping</b>
/shop - Browse our inventory
/cart - View your shopping cart
/checkout - Place your order

⚙️ <b>General</b>
/start - Welcome message
/help - Show this message

🔑 <b>Owner Only</b>
/addproduct - Add a new item to the shop
/set_owner - Claim bot ownership
"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)
