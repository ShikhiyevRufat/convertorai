from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🖼️ Convert Image Format", callback_data='convert_image')],
        [InlineKeyboardButton("📄 Convert Documents to PDF", callback_data='convert_document')],
        [InlineKeyboardButton("📲 Generate QR Code", callback_data='generate_qr')],
        [InlineKeyboardButton("📷 Instagram Post or Reel Download", callback_data='instagram_download')],
        [InlineKeyboardButton("🎵 Tiktok Reel Download", callback_data='tiktok_download')],
        [InlineKeyboardButton("🎥 YouTube MP3 or MP4 Download", callback_data='youtube_download')]
    ]

    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👋Welcome!  Which specialty do you want to use?",
        reply_markup=markup
    ) 