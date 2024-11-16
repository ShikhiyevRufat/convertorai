from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyboard = [
        ["📲 Start", "ℹ️ Help", "⚙️ Settings"],
        ["🔙 Back to Menu"]  
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    text = """
👋 Welcome! I can assist you with various tasks:
    
- 📷 Image Conversion
- 📄 Document to PDF Conversion
- 📲 QR Code Generation
- 🎥 YouTube MP3/MP4 Downloads
- 📱 Instagram and TikTok Downloads

Tap on a button below to get started!
    """
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=markup
    )
