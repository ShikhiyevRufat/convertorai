from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from io import BytesIO
from function.image_convertor import convert_image
from function.document_convertor import document_convertor
from function.qr_generate import qr_generate
from function.tiktok_downloander import download_tiktok
from function.youtube_downloander import download_youtube_or_tiktok_video
from user_credit import Credit
from utilities.start_func import start as start_func
from utilities.language_func import language as lang_func
from utilities.translations import translations
from utilities.language_func import user_language
from function.font_style import Fonts
from pyrogram import Client, filters
from function.bg_remover import process_image
import os
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
    
    elif query.data == 'bg_remove':
        user_state[query.from_user.id] = 'bg_remove'
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

    elif query.data == 'font_style':
        user_state[query.from_user.id] = 'font_style'
        await query.edit_message_text(f"{menu["pls_write_message"]}")    
    

    elif query.data.startswith('format_'):
        await handle_format_selection(update, context)
    elif query.data.startswith('quality_'):
        await handle_quality_selection(update, context)
    elif query.data.startswith('lang_'):
        lang_code = query.data.split('_')[1]
        user_language[query.from_user.id] = lang_code
        await start_func(update, context)
    elif query.data.startswith('style+'):
        # Extract style and apply it
        _, style = query.data.split('+')
        original_message = user_state.get(query.from_user.id)

        if original_message:
            styled_message = handle_style(style, original_message)
            await query.edit_message_text(styled_message)
            await query.message.reply_text(f"{menu["font_success"]}", reply_markup=success_start(update, context))
            # Clear the user state after processing
            del user_state[query.from_user.id]
        else:
            await query.edit_message_text("Please write a message first!",)

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
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def success_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    user_id = None
    
    if update.message:
        user_id = update.message.from_user.id
    elif update.callback_query:
        user_id = update.callback_query.from_user.id

    if user_id is None:
        raise ValueError("Unable to determine user ID")

    lang = user_language.get(user_id, "en")
    menu = translations[lang]

    keyboard = [
        [
            InlineKeyboardButton(f"{menu['start']}", callback_data='start'),
            InlineKeyboardButton(f"{menu['language']}", callback_data='language'),
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    return markup

def sanitize_filename(filepath):
    directory, filename = os.path.split(filepath)
    sanitized_filename = re.sub(r'[<>:"/\\|?*]', '', filename).replace(' ', '_')
    return os.path.join(directory, sanitized_filename)

def generate_buttons():
    buttons = [[
        InlineKeyboardButton('𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛', callback_data='style+typewriter'),
        InlineKeyboardButton('𝕆𝕦𝕥𝕝𝕚𝕟𝕖', callback_data='style+outline'),
        InlineKeyboardButton('𝐒𝐞𝐫𝐢𝐟', callback_data='style+serif'),
        ],[
        InlineKeyboardButton('𝑺𝒆𝒓𝒊𝒇', callback_data='style+bold_cool'),
        InlineKeyboardButton('𝑆𝑒𝑟𝑖𝑓', callback_data='style+cool'),
        InlineKeyboardButton('Sᴍᴀʟʟ Cᴀᴘs', callback_data='style+small_cap'),
        ],[
        InlineKeyboardButton('𝓈𝒸𝓇𝒾𝓅𝓉', callback_data='style+script'),
        InlineKeyboardButton('𝓼𝓬𝓻𝓲𝓹𝓽', callback_data='style+script_bolt'),
        InlineKeyboardButton('ᵗⁱⁿʸ', callback_data='style+tiny'),
        ],[
        InlineKeyboardButton('ᑕOᗰIᑕ', callback_data='style+comic'),
        InlineKeyboardButton('𝗦𝗮𝗻𝘀', callback_data='style+sans'),
        InlineKeyboardButton('𝙎𝙖𝙣𝙨', callback_data='style+slant_sans'),
        ],[
        InlineKeyboardButton('𝘚𝘢𝘯𝘴', callback_data='style+slant'),
        InlineKeyboardButton('𝖲𝖺𝗇𝗌', callback_data='style+sim'),
         InlineKeyboardButton('Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎', callback_data='style+circles'),
        ],[
        InlineKeyboardButton('🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎', callback_data='style+circle_dark'),
        InlineKeyboardButton('𝔊𝔬𝔱𝔥𝔦𝔠', callback_data='style+gothic'),
        InlineKeyboardButton('𝕲𝖔𝖙𝖍𝖎𝖈', callback_data='style+gothic_bolt'),
        ],[
        InlineKeyboardButton('C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡', callback_data='style+cloud'),
        InlineKeyboardButton('H̆̈ă̈p̆̈p̆̈y̆̈', callback_data='style+happy'),
        InlineKeyboardButton('S̑̈ȃ̈d̑̈', callback_data='style+sad'),
        ],[
            InlineKeyboardButton('🇸 🇵 🇪 🇨 🇮 🇦 🇱 ', callback_data='style+special'),
            InlineKeyboardButton('🅂🅀🅄🄰🅁🄴🅂', callback_data='style+squares'),
            InlineKeyboardButton('🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎', callback_data='style+squares_bold'),
            ],[
            InlineKeyboardButton('ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ', callback_data='style+andalucia'),
            InlineKeyboardButton('爪卂几ᘜ卂', callback_data='style+manga'),
            InlineKeyboardButton('S̾t̾i̾n̾k̾y̾', callback_data='style+stinky'),
            ],[
            InlineKeyboardButton('B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ', callback_data='style+bubbles'),
            InlineKeyboardButton('U͟n͟d͟e͟r͟l͟i͟n͟e͟', callback_data='style+underline'),
            InlineKeyboardButton('꒒ꍏꀷꌩꌃꀎꁅ', callback_data='style+ladybug'),
            ],[
            InlineKeyboardButton('R҉a҉y҉s҉', callback_data='style+rays'),
            InlineKeyboardButton('B҈i҈r҈d҈s҈', callback_data='style+birds'),
            InlineKeyboardButton('S̸l̸a̸s̸h̸', callback_data='style+slash'),
            ],[
            InlineKeyboardButton('s⃠t⃠o⃠p⃠', callback_data='style+stop'),
            InlineKeyboardButton('S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆', callback_data='style+skyline'),
            InlineKeyboardButton('A͎r͎r͎o͎w͎s͎', callback_data='style+arrows'),
            ],[
            InlineKeyboardButton('ዪሀክቿነ', callback_data='style+qvnes'),
            InlineKeyboardButton('S̶t̶r̶i̶k̶e̶', callback_data='style+strike'),
            InlineKeyboardButton('F༙r༙o༙z༙e༙n༙', callback_data='style+frozen')
            ]]
    return InlineKeyboardMarkup(buttons)

def handle_style(style, text):
    style_map = {
    'typewriter': Fonts.typewriter,
    'outline': Fonts.outline,
    'serif': Fonts.serief,
    'bold_cool': Fonts.bold_cool,
    'cool': Fonts.cool,
    'small_cap': Fonts.smallcap,
    'script': Fonts.script,
    'script_bolt': Fonts.bold_script,
    'tiny': Fonts.tiny,
    'comic': Fonts.comic,
    'sans': Fonts.san,
    'slant_sans': Fonts.slant_san,
    'slant': Fonts.slant,
    'sim': Fonts.sim,
    'circles': Fonts.circles,
    'circle_dark': Fonts.dark_circle,
    'gothic': Fonts.gothic,
    'gothic_bolt': Fonts.bold_gothic,
    'cloud': Fonts.cloud,
    'happy': Fonts.happy,
    'sad': Fonts.sad,
    'special': Fonts.special,
    'squares': Fonts.square,
    'squares_bold': Fonts.dark_square,
    'andalucia': Fonts.andalucia,
    'manga': Fonts.manga,
    'stinky': Fonts.stinky,
    'bubbles': Fonts.bubbles,
    'underline': Fonts.underline,
    'ladybug': Fonts.ladybug,
    'rays': Fonts.rays,
    'birds': Fonts.birds,
    'slash': Fonts.slash,
    'stop': Fonts.stop,
    'skyline': Fonts.skyline,
    'arrows': Fonts.arrows,
    'qvnes': Fonts.rvnes,
    'strike': Fonts.strike,
    'frozen': Fonts.frozen,
}
    cls = style_map.get(style)
    return cls(text) if cls else text

@Client.on_callback_query(filters.regex('^style'))
async def apply_style(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in user_state:
        await callback_query.answer("Please send a message first!", show_alert=True)
        return

    # Extract the chosen style
    _, style = callback_query.data.split('+')
    original_message = user_state[user_id]

    # Apply the chosen style to the message
    styled_message = handle_style(style, original_message)

    # Send the styled message
    await callback_query.message.edit_text(
        styled_message,
        reply_markup=callback_query.message.reply_markup
    )

    # Optionally, clear the stored message after processing
    del user_state[user_id]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id 
    lang = user_language.get(user_id, "en")
    query = update.callback_query

    menu = translations[lang]

    # if not await check_credits(update, context):
    #     return
    if user_state.get(user_id) == 'languages':
        await lang_func(update, context)

    if user_state.get(user_id) == 'starts':
        await start_func(update, context)
    
    if user_state.get(user_id) == 'font_style':
        if update.message:  
            user_state[user_id] = update.message.text  
            await update.message.reply_text(
                "Choose your style, please:",
                reply_markup=generate_buttons()
            )
        else:
            await update.message.reply_text("Please send a valid message first.")

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
            await update.message.reply_text(f"{menu["download_success"]}",reply_markup=success_start(update, context))
        except Exception as e:
            await update.message.reply_text(f"{menu["error_video"]}",reply_markup=success_start(update, context))
        user_state[user_id] = None

    if user_state.get(user_id) == 'awaiting_qr_input':
        text = update.message.text
        try:
            qr_code = qr_generate(text)
            await update.message.reply_photo(photo=qr_code, caption=f"{menu["download_success"]}",reply_markup=success_start(update, context)) 
        except Exception as e:
            await update.message.reply_text(f"{menu["error_qr"]}",reply_markup=success_start(update, context))

    elif user_state.get(user_id) == 'bg_remove':
        if update.message.photo:
            photo_file = await update.message.photo[-1].get_file()
            photo = await photo_file.download_as_bytearray()

            try:
                output_buffer = process_image(photo)

                await update.message.reply_document(document=output_buffer, caption=f"{menu["download_success"]}", filename="output_image.png", reply_markup=success_start(update, context))

            except Exception as e:
                await update.message.reply_text(f"{menu["error_image"]}")
        else:
            await update.message.reply_text(f"{menu["error_upload_image"]}")

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
            await update.message.reply_text(f"{menu["error_upload_image"]}",reply_markup=success_start(update, context))

    if user_state.get(user_id) == 'awaiting_document_upload':
        if update.message.document:
            document_file = await update.message.document.get_file()
            document_bytes = await document_file.download_as_bytearray()

            user_documents[user_id] = document_bytes

            await update.message.reply_text(f"{menu['converting_document']}")

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
                await update.message.reply_text(f"{menu['download_success']}", reply_markup=success_start(update, context))
            except FileNotFoundError:
                # Specific error handling for missing output file
                await update.message.reply_text(
                    f"{menu['error_format_document']}", reply_markup=success_start(update, context)
                )
            except Exception as e:
                # General error handling
                await update.message.reply_text(f"{menu['error_document']}",reply_markup=success_start(update, context))

            user_state[user_id] = None
            user_documents.pop(user_id, None)
        else:
            await update.message.reply_text(f"{menu['error_upload_document']}",reply_markup=success_start(update, context))

            
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
        await update.message.reply_text(f"{menu['select_format_quality']}", reply_markup=markup)

        # Update state
        user_state[user_id] = 'awaiting_youtube_selection'

def is_file_non_empty(filepath):
    return os.path.exists(filepath) and os.path.getsize(filepath) > 0

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

            filepath = download_youtube_or_tiktok_video(url, 'mp3')
            print(filepath)
            
            if filepath and is_file_non_empty(filepath):
                try:
                    with open(filepath, 'rb') as file:
                        await context.bot.send_audio(chat_id=query.message.chat_id, audio=file, title="Converted MP3")
                    # Credit.deduct_credits(user_id, 1)
                        await query.edit_message_text(f"{menu["download_success"]}",reply_markup=success_start(update, context))
                except Exception as e:
                    print(f"Error sending MP3 file: {e}")
                    await query.edit_message_text(f"{menu["error_music"]}",reply_markup=success_start(update, context))
                finally:
                    os.remove(filepath)
            else:
                await query.edit_message_text(f"{menu["error_music_retry"]}", reply_markup=success_start(update, context))
            user_state[user_id] = None
            user_youtube_urls.pop(user_id, None)
        else:
            await query.edit_message_text(f"{menu["no_youtube_url"]}",reply_markup=success_start(update, context))

        user_state[user_id] = None


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
        await query.edit_message_text(f"{menu["download_success"]}",reply_markup=success_start(update, context))

        user_state[user_id] = None
        user_images.pop(user_id, None)
    else:
        await query.edit_message_text(f"{menu["no_youtube_url"]}",reply_markup=success_start(update, context))

async def handle_quality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = user_language.get(user_id, "en")

    menu = translations[lang]
    
    if user_state.get(user_id) == 'awaiting_starts':
        start_func(update, context)

    if user_state.get(user_id) == 'awaiting_youtube_selection':
        url = user_youtube_urls.get(user_id)
        if not url:
            await query.edit_message_text(f"{menu['no_youtube_url']}",reply_markup=success_start(update, context))
            return

        if query.data.startswith('quality_'):
            resolution = query.data.split('_')[1]
            format_choice = f'mp4_{resolution}'

            await query.edit_message_text(f"{menu['please_wait_mp4']}")

            filepath = download_youtube_or_tiktok_video(url, format_choice)
            if filepath:
                print(f"Original file path from downloader: {filepath}")

                sanitized_filepath = sanitize_filename(filepath)
                if filepath != sanitized_filepath:
                    if not os.path.exists(sanitized_filepath):
                        os.rename(filepath, sanitized_filepath)
                    filepath = sanitized_filepath  

                if os.path.isfile(filepath):
                    try:
                        with open(filepath, 'rb') as video_file:
                            await context.bot.send_video(chat_id=query.message.chat_id, video=video_file)
                            await query.edit_message_text(f"{menu['download_success']}", reply_markup=success_start(update, context))
                    except Exception as e:
                        print(f"Error sending MP4 file: {e}")
                        await query.edit_message_text(f"{menu["error_video"]}")
                    finally:
                        os.remove(filepath)  
                else:
                    await query.edit_message_text("File does not exist or download failed.")
            else:
                await query.edit_message_text(f"{menu["error_convert_video"]}", reply_markup=success_start(update, context))

            user_state[user_id] = None
            user_youtube_urls.pop(user_id, None)

        else:
            await query.edit_message_text(f"{menu['error_youtube_url']}", reply_markup=success_start(update, context))

# sudo systemctl daemon-reload
# sudo systemctl restart telegrambot
# sudo journalctl -u telegrambot -f
# sudo nano /etc/systemd/system/telegrambot.service
