from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update, ReplyKeyboardMarkup
from bot_system import button_callback, handle_message
from dotenv import load_dotenv
import os


def configure():
    load_dotenv()

TOKEN = os.getenv("token")

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the interface when 'Back' is clicked."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Returning to the main menu. Use 📲 Start to begin again."
    )
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📲 Start", "ℹ️ Help", "⚙️ Settings"],
        ["🔙 Back to Menu"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    text = "Welcome to the bot! Use the menu below to navigate."
    await context.bot.send_message(update.effective_chat.id, text, reply_markup=markup)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔙 Back to Menu"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    text = "This is the Help section, explaining the bot's capabilities."
    await context.bot.send_message(update.effective_chat.id, text, reply_markup=markup)

def main():
    application = Application.builder().token(TOKEN).read_timeout(60).build()
    application.add_handler(CommandHandler("📲 Start", start))
    application.add_handler(CommandHandler("ℹ️ Help", help))
    application.add_handler(CommandHandler("🔙 Back to Menu", back_to_menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    application.add_handler(MessageHandler(filters.ATTACHMENT, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main() 