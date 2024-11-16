from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import Update, ReplyKeyboardMarkup
from bot_system import button_callback, handle_message
from utilities.help_func import help as help_func
from utilities.start_func import start as start_func
from dotenv import load_dotenv
import os


def configure():
    load_dotenv()


TOKEN = os.getenv("token")


# Start Menu
async def start_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Initial menu when the bot starts."""
    keyboard = [
        ["📲 Start", "ℹ️ Help", "⚙️ Settings"],
        ["🔙 Back to Menu"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    text = "Welcome to the bot! Use the menu below to navigate."
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=markup
    )


# Back to Menu Handler
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the interface when 'Back to Menu' is clicked."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Returning to the main menu. Use 📲 Start to begin again."
    )


def main():
    configure()

    # Create Application
    application = Application.builder().token(TOKEN).read_timeout(60).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start_now))  # Initial /start command

    # Message Handlers for Button Clicks
    application.add_handler(MessageHandler(filters.Regex("^📲 Start$"), start_func))  # Start button
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ Help$"), help_func))  # Help button
    application.add_handler(MessageHandler(filters.Regex("^🔙 Back to Menu$"), back_to_menu))  # Back button

    application.add_handler(CallbackQueryHandler(button_callback))


    # Other Handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))
    application.add_handler(MessageHandler(filters.ATTACHMENT, handle_message))

    # Start Polling
    application.run_polling()


if __name__ == "__main__":
    main()
