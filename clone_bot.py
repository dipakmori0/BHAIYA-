import telebot
BOT_USERNAME = "Hahwjahjjahabot"

# Simple clone bot example
def start_clone(token, user):
    bot = telebot.TeleBot(token)
    bot.send_message(user, f"🤖 Clone of @{BOT_USERNAME} activated!")
    bot.infinity_polling()
