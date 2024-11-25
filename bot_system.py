from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from io import BytesIO
import os
from function.image_convertor import convert_image
from function.document_convertor import document_convertor
from function.instagram_downloander import instagram_downloader
from function.qr_generate import qr_generate
from function.tiktok_downloander import download_tiktok
from youtube_downloander import youtube_downloader
from user_credit import Credit
from utilities.start_func import start as start_func
from utilities.language_func import language as lang_func
from utilities.translations import translations
from utilities.language_func import user_language
from yt_download.main import Ytube
import re

user_state = {}
user_images = {}
user_youtube_urls = {}
user_documents = {}
user_credits = {}
INITIAL_CREDITS = 30


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_chat.id
    lang = user_language.get(user_id, "en")

    menu = translations[lang]
    query = update.callback_query
    await query.answer()

    if query.data == 'convert_image':
        user_state[query.from_user.id] = 'awaiting_image_upload'
        await query.edit_message_text(f"{menu["please_image_upload"]}")

    elif query.data == 'convert_document':
        user_state[query.from_user.id] = 'awaiting_document_upload'
        await query.edit_message_text(f"{menu["please_document_upload"]}")

    elif query.data == 'start':
        user_state[query.from_user.id] = 'starts'
        await start_func(update, context) 

    elif query.data == 'language':
        await lang_func(update, context)

    elif query.data == 'generate_qr':
        user_state[query.from_user.id] = 'awaiting_qr_input'
        await query.edit_message_text(f"{menu["please_enter_qr"]}")

    elif query.data == 'tiktok_download':
        user_state[query.from_user.id] = 'awaiting_tiktok_url'
        await query.edit_message_text(f"{menu["please_send_tiktok"]}")

    elif query.data == 'youtube_download':
        user_state[query.from_user.id] = 'awaiting_youtube_url'
        await query.edit_message_text(f"{menu["please_send_youtube"]}")

    elif query.data.startswith('format_'):
        await handle_format_selection(update, context)
    elif query.data.startswith('quality_'):
        await handle_quality_selection(update, context)
    elif query.data.startswith('lang_'):
        lang_code = query.data.split('_')[1]
        user_language[query.from_user.id] = lang_code
        await start_func(update, context)
    else:
        await query.edit_message_text("This function is not available.")

# async def check_credits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
#     user_id = update.message.from_user.id
#     Credit.add_user(user_id) 

#     if Credit.get_credits(user_id) <= 0:
#         await update.message.reply_text("😪You have no credits left. Please pay to continue using the bot.")
#         return False

#     return True

# async def refill_credits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     user_id = update.message.from_user.id
#     Credit.reset_credits(user_id)
#     await update.message.reply_text(f"Your credits have been refilled! 💎 You now have {Credit.INITIAL_CREDITS} credits.")
def success_start():
        keyboard = [
            [InlineKeyboardButton("Start", callback_data='start'),InlineKeyboardButton("Language", callback_data='language')],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        return markup
    


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    lang = user_language.get(user_id, "en")

    menu = translations[lang]

    # if not await check_credits(update, context):
    #     return
    if user_state.get(user_id) == 'languages':
        await lang_func(update, context)

    if user_state.get(user_id) == 'starts':
        await start_func(update, context)

    if user_state.get(user_id) == 'awaiting_tiktok_url':
        url = update.message.text
        await update.message.reply_text(f"{menu["tiktok_download_video"]}")

        output_filename = 'tiktok_video.mp4'
        target_resolution = '720p'  

        try:
            download_tiktok(url, output_filename, target_resolution)
            with open(output_filename, 'rb') as video_file:
                await context.bot.send_video(chat_id=update.effective_chat.id, video=video_file)
            os.remove(output_filename)  
            # Credit.deduct_credits(user_id, 1)
            # await update.message.reply_text(f"🥳Download successful! \n💎 Your credits:  {Credit.get_credits(user_id)}/30 (+1) \nFor using the bot again, please write /start.")
            await update.message.reply_text(f"{menu["download_success"]}",reply_markup=success_start())
        except Exception as e:
            await update.message.reply_text(f"Error downloading video: {e}")
        user_state[user_id] = None

    if user_state.get(user_id) == 'awaiting_qr_input':
        text = update.message.text
        try:
            qr_code = qr_generate(text)
            await update.message.reply_photo(photo=qr_code, caption=f"{menu["download_success"]}",reply_markup=success_start()) 
        except Exception as e:
            update.message.reply_text(f"Error generating or sending QR code: {e}")


    elif user_state.get(user_id) == 'awaiting_image_upload':
        if update.message.photo:
            photo_file = await update.message.photo[-1].get_file()
            photo = await photo_file.download_as_bytearray()

            user_images[user_id] = photo

            keyboard = [
            [
                InlineKeyboardButton("PNG", callback_data='format_png'),
                InlineKeyboardButton("JPEG", callback_data='format_jpeg'),
                InlineKeyboardButton("GIF", callback_data='format_gif')
            ],
            [
                InlineKeyboardButton("TIFF", callback_data='format_tiff'),
                InlineKeyboardButton("PDF", callback_data='format_pdf'),
                InlineKeyboardButton("AVIF", callback_data='format_avif')
            ],
            [
                InlineKeyboardButton("WEBP", callback_data='format_webp')
            ]
        ]

            markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"{menu["choose_image_format"]}",
                reply_markup=markup
            )
            user_state[user_id] = 'awaiting_format_selection'
        else:
            await update.message.reply_text(f"{menu["error_upload_image"]}")

    if user_state.get(user_id) == 'awaiting_document_upload':
        if update.message.document:
            document_file = await update.message.document.get_file()
            document_bytes = await document_file.download_as_bytearray()

            user_documents[user_id] = document_bytes

            await update.message.reply_text(f"{menu["converting_document"]}")

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
                # Credit.deduct_credits(user_id, 1)
                await update.message.reply_text(f"{menu["download_success"]}",reply_markup=success_start())
            except Exception as e:
                await update.message.reply_text(f"Error during document conversion: {e}")

            user_state[user_id] = None
            user_documents.pop(user_id, None)
        else:
            await update.message.reply_text(f"{menu["error_upload_document"]}")
            
    elif user_state.get(user_id) == 'awaiting_youtube_url':
        url = update.message.text
        user_youtube_urls[user_id] = url

        keyboard = [
            [InlineKeyboardButton("🔊MP3", callback_data='format_mp3')],
            [InlineKeyboardButton("📹MP4 - 360p", callback_data='quality_360')],
            [InlineKeyboardButton("📹MP4 - 720p", callback_data='quality_720')],
            [InlineKeyboardButton("📹MP4 - 1080p", callback_data='quality_1080')],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"{menu["select_format_quality"]}",
            reply_markup=markup
        )
        user_state[user_id] = 'awaiting_youtube_selection'

async def handle_format_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = user_language.get(user_id, "en")

    menu = translations[lang]

    if user_state.get(user_id) == 'awaiting_youtube_selection' and query.data == 'format_mp3':
        url = user_youtube_urls.get(user_id)
        if url:
            await query.edit_message_text(f"{menu["please_wait_mp3"]}")

            filepath = youtube_downloader(url, 'mp3')
            if filepath and os.path.exists(filepath):
                try:
                    with open(filepath, 'rb') as file:
                        await context.bot.send_audio(chat_id=query.message.chat_id, audio=file, title="Converted MP3")
                    # Credit.deduct_credits(user_id, 1)
                    await query.edit_message_text(f"{menu["download_success"]}",reply_markup=success_start())
                except Exception as e:
                    print(f"Error sending MP3 file: {e}")
                    await query.edit_message_text(f"Failed to send MP3 file: {e}")
                finally:
                    os.remove(filepath)
                    user_state[user_id] = None  
                    user_youtube_urls.pop(user_id, None)
            else:
                await query.edit_message_text("Failed to convert to MP3.")
            user_state[user_id] = None
            user_youtube_urls.pop(user_id, None)
        else:
            await query.edit_message_text(f"{menu["no_youtube_url"]}")

        user_state[user_id] = None
        user_images.pop(user_id, None)

    elif user_state.get(user_id) == 'awaiting_format_selection' and user_id in user_images:
        await query.edit_message_text(f"{menu["please_wait_image"]}")

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
        # Credit.deduct_credits(user_id, 1)
        await query.edit_message_text(f"{menu["download_success"]}",reply_markup=success_start())

        user_state[user_id] = None
        user_images.pop(user_id, None)
    else:
        await query.edit_message_text(f"{menu["no_youtube_url"]}")

def sanitize_filename(filepath):
    directory, filename = os.path.split(filepath)
    sanitized_filename = re.sub(r'[<>:"/\\|?*]', '', filename).replace(' ', '_')
    return os.path.join(directory, sanitized_filename)


async def handle_quality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = user_language.get(user_id, "en")

    menu = translations[lang]

    if user_state.get(user_id) == 'awaiting_tiktok_url':
        url = update.message.text
        resolution = query.data.split('_')[1]
        output_filename = 'tiktok_video.mp4'

        try:
            download_tiktok(url, output_filename, target_resolution=resolution)
            
            with open(output_filename, 'rb') as video_file:
                await context.bot.send_video(chat_id=query.message.chat_id, video=video_file)
            os.remove(output_filename)
            
            Credit.deduct_credits(user_id, 1)
            await query.edit_message_text(f"{menu["download_success"]}",reply_markup=success_start())
        except Exception as e:
            await query.edit_message_text(f"Error downloading video: {e}")
        finally:
            user_state[user_id] = None
            user_images.pop(user_id, None)
    
    if user_state.get(user_id) == 'awaiting_starts':
        start_func(update, context)

    if user_state.get(user_id) == 'awaiting_youtube_selection':
        url = user_youtube_urls.get(user_id)
        if not url:
            await query.edit_message_text(f"{menu['no_youtube_url']}")
            return

        if query.data.startswith('quality_'):
            resolution = query.data.split('_')[1]

            await query.edit_message_text(f"{menu['please_wait_mp4']}")

            # Download the video
            filepath = youtube_downloader(url, 'mp4', resolution)
            if filepath:
                print(f"Original file path from downloader: {filepath}")

                # Sanitize the file path
                sanitized_filepath = sanitize_filename(filepath)
                if filepath != sanitized_filepath:
                    if not os.path.exists(sanitized_filepath):
                        os.rename(filepath, sanitized_filepath)
                    filepath = sanitized_filepath  # Update the file path to sanitized path

                # Send the video file
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, 'rb') as video_file:
                            await context.bot.send_video(chat_id=query.message.chat_id, video=video_file)
                        await query.edit_message_text(f"{menu['download_success']}", reply_markup=success_start())
                    except Exception as e:
                        print(f"Error sending MP4 file: {e}")
                        await query.edit_message_text("Failed to send MP4 file.")
                    finally:
                        os.remove(filepath)  # Clean up the file
                else:
                    await query.edit_message_text("File does not exist or download failed.")
            else:
                await query.edit_message_text("Failed to download the video.")

            user_state[user_id] = None
            user_youtube_urls.pop(user_id, None)

        else:
            await query.edit_message_text(f"{menu['no_youtube_url']}")



# sudo systemctl daemon-reload
# sudo systemctl restart telegrambot
# sudo journalctl -u telegrambot -f
# sudo nano /etc/systemd/system/telegrambot.service
