from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the persistent keyboard for the main menu
    keyboard = [
        ["🔙 Back to Menu", "📲 Start"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    # The help message with information
    text = """
ℹ️ Here’s the list of features available:

📷 **Supported Images**: png, jpg, jpeg, gif, tiff, pdf, avif, webp  
📃 **Supported Documents**: XLSX, XLS, DOC, DOCX, PPTX, PPT, PDF  
🎥 **YouTube Downloads**: MP3 and MP4  
💎 **TikTok Downloads**: Reels  
💡  **Instagram Downloads**: Post and Video  
    """
    
    # Send the help message with the persistent menu
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=markup
    )
