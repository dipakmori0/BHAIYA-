import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ✅ Bot token
BOT_TOKEN = "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c"
bot = telebot.TeleBot(BOT_TOKEN)

# Channels ID list
CHANNELS = [-1002851939876, -1002321550721]

# Check if user joined all channels
def is_user_joined(user_id):
    for channel_id in CHANNELS:
        try:
            member = bot.get_chat_member(channel_id, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if not is_user_joined(user_id):
        text = "❌ You must join our channels first!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 1", url="https://t.me/+eB_J_ExnQT0wZDU9"))
        markup.add(InlineKeyboardButton("Join Channel 2", url="https://t.me/taskblixosint"))
        bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    # VIP welcome message
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Start VIP", callback_data="start_vip"))
    bot.send_message(message.chat.id, "👋 Welcome VIP User!\nClick below to start:", reply_markup=markup)

# Callback handler for Start VIP button
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "start_vip":
        bot.send_message(call.message.chat.id, "✅ You are verified! Let's begin your VIP session.")

# Run bot
bot.infinity_polling()
