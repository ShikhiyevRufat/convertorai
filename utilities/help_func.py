from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utilities.start_func import start  # Import the start function from start.py

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the help message with a persistent menu."""
    keyboard = [
        ["🔙 Back to Menu", "📲 Start"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    text = """
ℹ️ Here’s the list of features available:

📷 **Supported Images**: png, jpg, jpeg, gif, tiff, pdf, avif, webp  
📃 **Supported Documents**: XLSX, XLS, DOC, DOCX, PPTX, PPT, PDF  
🎥 **YouTube Downloads**: MP3 and MP4  
💎 **TikTok Downloads**: Reels  
💡  **Instagram Downloads**: Post and Video  
    """
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=markup
    )

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the '🔙 Back to Menu' button by clearing the interface."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Returning to the main menu. Use /start to begin again."
    )

async def handle_help_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles actions for buttons in the help menu."""
    user_input = update.message.text

    if user_input == "🔙 Back to Menu":
        await back_to_menu(update, context)
    elif user_input == "📲 Start":
        await start(update, context)
