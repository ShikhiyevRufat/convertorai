from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

# Import functions
from utilities.start_func import start as start_command
from utilities.help_func import help as help_command, handle_help_buttons

def configure():
    load_dotenv()

TOKEN = os.getenv("token")

def main():
    configure()
    application = Application.builder().token(TOKEN).read_timeout(60).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Message Handlers
    application.add_handler(MessageHandler(filters.Regex("🔙 Back to Menu") | filters.Regex("📲 Start"), handle_help_buttons))

    application.run_polling()

if __name__ == '__main__':
    main()
