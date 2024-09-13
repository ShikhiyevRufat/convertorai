from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from PIL import Image
from io import BytesIO
import os
from image_convertor import convert_image
from document_convertor import document_convertor
from instagram_downloander import instagram_downloander
from qr_generate import qr_generate
from tiktok_downloander import download_tiktok
from youtube_downloander import youtube_downloander

TOKEN = '7503452735:AAHe7RPN_9GpaVWU4JYjmKG68Boq39hDljM'

user_state = {}
user_images = {}
user_youtube_urls = {}
user_documents = {}

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

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome! Which specialty do you want to use?",
        reply_markup=markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'convert_image':
        user_state[query.from_user.id] = 'awaiting_image_upload'
        await query.edit_message_text("Please upload the image you want to convert.")
    elif query.data == 'convert_document':
        user_state[query.from_user.id] = 'awaiting_document_upload'
        await query.edit_message_text("Please upload the document you want to convert to PDF.")

    elif query.data == 'instagram_download':

        keyboard = [
            [InlineKeyboardButton("Post or Reel", callback_data='instagram_post')]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Please choose whether you want to download Reels or Post.", reply_markup=markup)
    elif query.data == 'instagram_reels' or query.data == 'instagram_post':
        user_state[query.from_user.id] = query.data  
        await query.edit_message_text("Please send the Instagram URL.")

    elif query.data == 'generate_qr':
        user_state[query.from_user.id] = 'awaiting_qr_input'
        await query.edit_message_text("Please enter the text or URL for the QR code.")

    elif query.data == 'tiktok_download':
        user_state[query.from_user.id] = 'awaiting_tiktok_url'
        await query.edit_message_text("Please send me the TikTok video URL.")

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

    if user_state.get(user_id) == 'awaiting_tiktok_url':
        url = update.message.text
        await update.message.reply_text("Downloading TikTok video...")

        output_filename = 'tiktok_video.mp4'
        target_resolution = '720p'  

        try:
            download_tiktok(url, output_filename, target_resolution)
            with open(output_filename, 'rb') as video_file:
                await context.bot.send_video(chat_id=update.effective_chat.id, video=video_file)
            os.remove(output_filename)  
            await update.message.reply_text("Download successful! For using the bot again, please write /start.")
        except Exception as e:
            await update.message.reply_text(f"Error downloading video: {e}")
        user_state[user_id] = None

    if user_state.get(user_id) == 'awaiting_qr_input':
        text = update.message.text
        qr_code = qr_generate(text)  
        await update.message.reply_photo(photo=qr_code, caption="Here is your QR code. For using the bot again, please write /start.")
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

    if user_state.get(user_id) == 'awaiting_document_upload':
        if update.message.document:
            document_file = await update.message.document.get_file()
            document_bytes = await document_file.download_as_bytearray()

            user_documents[user_id] = document_bytes

            await update.message.reply_text("Converting your document to PDF. Please wait...")

            try:
                input_file_path = 'uploaded_document' + os.path.splitext(update.message.document.file_name)[1]
                output_file_path = 'uploaded_document.pdf'

                with open(input_file_path, 'wb') as f:
                    f.write(user_documents[user_id])

                document_convertor(input_file_path, output_file_path)

                with open(output_file_path, 'rb') as pdf_file:
                    await context.bot.send_document(chat_id=update.effective_chat.id, document=pdf_file)

                os.remove(input_file_path)
                os.remove(output_file_path)

                await update.message.reply_text("Document conversion successful! For using the bot again, please write /start.")
            except Exception as e:
                await update.message.reply_text(f"Error during document conversion: {e}")

            user_state[user_id] = None
            user_documents.pop(user_id, None)
        else:
            await update.message.reply_text("Please upload a document.")


    elif user_state.get(user_id) == 'instagram_post':
        url = update.message.text
        content_type = 'post'
        await update.message.reply_text("Please wait 1 minute for loading...")
        
        media, media_type = instagram_downloander(url, content_type)

        if media and media_type:
            if media_type == 'video':
                await update.message.reply_video(video=media, filename='instagram_video.mp4')
            elif media_type == 'image':
                await update.message.reply_photo(photo=media, filename='instagram_image.jpg')
            else:
                await update.message.reply_text("Unsupported media type.")
            await update.message.reply_text(f"Download successful! For using the bot again, please write /start.")
        else:
            await update.message.reply_text("Failed to download the Instagram content.")
        user_state[user_id] = None
            
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
            await query.edit_message_text("Please wait 1 minute while your MP3 is being processed...")

            filepath = youtube_downloander(url, 'mp3')
            if filepath and os.path.exists(filepath):
                try:
                    with open(filepath, 'rb') as file:
                        await context.bot.send_audio(chat_id=query.message.chat_id, audio=file, title="Converted MP3")
                    await query.edit_message_text(f"Download successful: {filepath}, For using the bot again, please write /start.")
                except Exception as e:
                    print(f"Error sending MP3 file: {e}")
                    await query.edit_message_text("Failed to send MP3 file.")
                finally:
                    os.remove(filepath)
            else:
                await query.edit_message_text("Failed to convert to MP3.")
            user_state[user_id] = None
            user_youtube_urls.pop(user_id, None)
        else:
            await query.edit_message_text("No YouTube URL received.")
        try:
            if filepath and os.path.exists(filepath):
                with open(filepath, 'rb') as video_file:
                    await context.bot.send_video(chat_id=update.effective_chat.id, video=video_file)
                await update.message.reply_text(f"Download successful: {filepath}, For using the bot again, please write /start.")
                os.remove(filepath)  
            else:
                await update.message.reply_text("Failed to download the TikTok video.")
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}")

        user_state[user_id] = None

    elif user_state.get(user_id) == 'awaiting_format_selection' and user_id in user_images:
        await query.edit_message_text("Please wait 1 minute while your image is being processed...")

        input_image = BytesIO(user_images[user_id])
        output_format = query.data.split('_')[1]
        output_image = BytesIO()
        error_message = convert_image(input_image, output_image, output_format)

        if error_message:
            await query.edit_message_text(f"Error: {error_message}")
        else:
            output_image.seek(0)
            await context.bot.send_document(chat_id=query.message.chat_id, document=output_image,
                                            filename=f"converted.{output_format}")

        user_state[user_id] = None
        user_images.pop(user_id, None)
    else:
        await query.edit_message_text("Please upload an image first.")


async def handle_quality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_state.get(user_id) == 'awaiting_tiktok_url':
        url = update.message.text
        resolution = query.data.split('_')[1]  
        output_filename = 'tiktok_video.mp4'

        try:
            download_tiktok(url, output_filename, target_resolution=resolution)
            with open(output_filename, 'rb') as video_file:
                await context.bot.send_video(chat_id=query.message.chat_id, video=video_file)
            os.remove(output_filename)  
            await query.edit_message_text("Download successful! For using the bot again, please write /start.")
        except Exception as e:
            await query.edit_message_text(f"Error downloading video: {e}")
        user_state[user_id] = None

    if user_state.get(user_id) == 'awaiting_youtube_selection':
        url = user_youtube_urls.get(user_id)
        if not url:
            await query.edit_message_text("No YouTube URL received.")
            return

        if query.data.startswith('quality_'):
            resolution = query.data.split('_')[1]

            await query.edit_message_text("Please wait 1 minute while your video is being processed...")
            
            filepath = youtube_downloander(url, 'mp4', resolution)
            if filepath and os.path.exists(filepath):
                try:
                    with open(filepath, 'rb') as file:
                        await context.bot.send_video(chat_id=query.message.chat_id, video=file)
                    await query.edit_message_text(f"Download successful: {filepath}, For using the bot again, please write /start.")
                except Exception as e:
                    print(f"Error sending MP4 file: {e}")
                    await query.edit_message_text("Failed to send MP4 file.")
                finally:
                    os.remove(filepath)
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

    application.add_handler(MessageHandler(filters.ATTACHMENT, handle_message))

    # Start the bot
    application.run_polling()


if __name__ == '__main__':
    main()
