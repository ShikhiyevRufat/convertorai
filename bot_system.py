from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from PIL import Image
from io import BytesIO
import os
from image_convertor import convert_image
from document_convertor import document_convertor
from instagram_downloander import instagram_downloander
from qr_generate import qr_generate
from tiktok_downloander import tiktok_downloander
from youtube_downloander import youtube_downloander

TOKEN = '7503452735:AAHe7RPN_9GpaVWU4JYjmKG68Boq39hDljM'

user_state = {}
user_images = {}  
user_youtube_urls = {}  

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🖼️ Convert Image", callback_data='convert_image')],
        [InlineKeyboardButton("📄 Convert Document", callback_data='convert_document')],
        [InlineKeyboardButton("📷 Instagram Download", callback_data='instagram_download')],
        [InlineKeyboardButton("📲 Generate QR Code", callback_data='generate_qr')],
        [InlineKeyboardButton("🎵 Tiktok Download", callback_data='tiktok_download')],
        [InlineKeyboardButton("🎥 YouTube Download", callback_data='youtube_download')]
    ]

    markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome! Which specialty do you want to use?",
        reply_markup=markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'convert_image':
        user_state[query.from_user.id] = 'awaiting_image_upload'
        await query.edit_message_text("Please upload the image you want to convert.")
    elif query.data == 'convert_document':
        pass
    elif query.data == 'instagram_download':
        pass
    elif query.data == 'generate_qr':
        user_state[query.from_user.id] = 'awaiting_qr_input'
        await query.edit_message_text("Please enter the text or URL for the QR code.")
    elif query.data == 'tiktok_download':
        pass
    elif query.data == 'youtube_download':
        user_state[query.from_user.id] = 'awaiting_youtube_url'
        await query.edit_message_text("Please send me the YouTube video URL.")
    elif query.data.startswith('format_'):
        await handle_format_selection(update, context)
    elif query.data.startswith('quality_'):
        await handle_quality_selection(update, context)
    else:
        await query.edit_message_text("This function is not available.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    if user_state.get(user_id) == 'awaiting_qr_input':
        text = update.message.text
        qr_code = qr_generate(text)  
        await update.message.reply_photo(photo=qr_code, caption="Here is your QR code.")
        user_state[user_id] = None
        
    elif user_state.get(user_id) == 'awaiting_image_upload':
        if update.message.photo:
            photo_file = await update.message.photo[-1].get_file()
            photo = await photo_file.download_as_bytearray()

            user_images[user_id] = photo

            keyboard = [
                [InlineKeyboardButton("PNG", callback_data='format_png')],
                [InlineKeyboardButton("JPEG", callback_data='format_jpeg')],
                [InlineKeyboardButton("GIF", callback_data='format_gif')],
                [InlineKeyboardButton("TIFF", callback_data='format_tiff')],
                [InlineKeyboardButton("PDF", callback_data='format_pdf')],
                [InlineKeyboardButton("AVIF", callback_data='format_avif')],
                [InlineKeyboardButton("WEBP", callback_data='format_webp')],
            ]
            markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Which format do you want to convert the image to?",
                reply_markup=markup
            )
            user_state[user_id] = 'awaiting_format_selection'
        else:
            await update.message.reply_text("Please upload an image.")
            
    elif user_state.get(user_id) == 'awaiting_youtube_url':
        url = update.message.text
        user_youtube_urls[user_id] = url
        
        keyboard = [
            [InlineKeyboardButton("MP3", callback_data='format_mp3')],
            [InlineKeyboardButton("MP4 - 360", callback_data='quality_360')],
            [InlineKeyboardButton("MP4 - 720", callback_data='quality_720')],
            [InlineKeyboardButton("MP4 - 1080", callback_data='quality_1080')],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Select the format and quality you want to download:",
            reply_markup=markup
        )
        user_state[user_id] = 'awaiting_youtube_selection'

async def handle_format_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_state.get(user_id) == 'awaiting_youtube_selection' and query.data == 'format_mp3':
        url = user_youtube_urls.get(user_id)
        if url:
            filepath = youtube_downloander(url, 'mp3')
            if filepath and os.path.exists(filepath):
                with open(filepath, 'rb') as file:
                    await query.edit_message_text("MP3 conversion successful. Download your file:")
                    await query.message.reply_document(document=file, filename=f"converted.mp3")
            else:
                await query.edit_message_text("Failed to convert to MP3.")
            user_state[user_id] = None
            user_youtube_urls.pop(user_id, None)
        else:
            await query.edit_message_text("No YouTube URL received.")
    elif user_state.get(user_id) == 'awaiting_format_selection' and user_id in user_images:
        # Image conversion logic
        input_image = BytesIO(user_images[user_id])
        output_format = query.data.split('_')[1]  # Extract format (png, jpeg, etc.)
        output_image = BytesIO()  
        error_message = convert_image(input_image, output_image, output_format)

        if error_message:
            await query.edit_message_text(f"Error: {error_message}")
        else:
            output_image.seek(0)
            await query.edit_message_text("Image conversion successful. Download your file:")
            await query.message.reply_document(document=output_image, filename=f"converted.{output_format}")

        user_state[user_id] = None
        user_images.pop(user_id, None)
    else:
        await query.edit_message_text("Please upload an image first.")


async def handle_quality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_state.get(user_id) == 'awaiting_youtube_selection':
        url = user_youtube_urls.get(user_id)
        if not url:
            await query.edit_message_text("No YouTube URL received.")
            return

        resolution = query.data.split('_')[1]  # Extract the resolution (360p, 720p, etc.)
        filepath = youtube_downloander(url, 'mp4', resolution)
        
        if filepath and os.path.exists(filepath):
            with open(filepath, 'rb') as file:
                await query.message.reply_document(document=file, filename=os.path.basename(filepath))
            await query.edit_message_text(f"Download successful: {filepath}")
        else:
            await query.edit_message_text("Failed to download the video.")
        
        user_state[user_id] = None
        user_youtube_urls.pop(user_id, None)
    else:
        await query.edit_message_text("No YouTube URL received.")




def main():
    application = Application.builder().token(TOKEN).read_timeout(60).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
