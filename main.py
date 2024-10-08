from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from utilities.start_func import start
from utilities.help_func import help
from bot_system import button_callback, handle_message
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()

TOKEN = os.getenv("token")

def main():
    application = Application.builder().token(TOKEN).read_timeout(60).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    application.add_handler(MessageHandler(filters.ATTACHMENT, handle_message))

    application.run_polling()


if __name__ == '__main__':
    main()