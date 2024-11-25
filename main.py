from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler
from bot_system import button_callback, handle_message
from utilities.help_func import help as help_func
from utilities.language_func import language as lang
from config import TOKEN, configure
import os


def main():
    configure()

    application = Application.builder().token(TOKEN).read_timeout(300).build()

    application.add_handler(MessageHandler(filters.Regex("start"), lang)) 
    application.add_handler(MessageHandler(filters.Regex("help"), help_func))  

    application.add_handler(CallbackQueryHandler(button_callback))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))
    application.add_handler(MessageHandler(filters.ATTACHMENT, handle_message))

    application.run_polling()


if __name__ == "__main__":
    main()
