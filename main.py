from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update, ReplyKeyboardMarkup

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
    application = Application.builder().token("YOUR_BOT_TOKEN").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.run_polling()

if __name__ == '__main__':
    main()
