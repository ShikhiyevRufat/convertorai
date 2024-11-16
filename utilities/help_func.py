from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=HelpText.text
    )
class HelpText :
    text = """
    Get information about our bot.
    20 Supported files:

    📷 Images (8)
    png, jpg, jpeg, gif, tiff, pdf, avif, webp

    💼 Document (7)
    XLSX, XLS, DOC, DOCX, PPTX, PPT, PDF

    🎥 Youtube downloaded (2)
    MP3 and MP4

    📱 TikTok download (1)
    Reels

    📱 Instagram download (2)
    Video and Post

    """
