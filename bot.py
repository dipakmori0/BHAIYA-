import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c"
bot = telebot.TeleBot(BOT_TOKEN)

CHANNELS = [-1002851939876, -1002321550721]

def is_user_joined(user_id):
    for channel_id in CHANNELS:
        try:
            member = bot.get_chat_member(channel_id, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if not is_user_joined(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 1", url="https://t.me/+eB_J_ExnQT0wZDU9"))
        markup.add(InlineKeyboardButton("Join Channel 2", url="https://t.me/taskblixosint"))
        bot.send_message(message.chat.id, "❌ You must join our channels first!", reply_markup=markup)
        return

    # Channels joined → show Joined CHENAL message
    bot.send_message(message.chat.id, "✅ Joined CHENAL\n✅ Joined CHENAL")

    # VIP + Verify buttons
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Verify", callback_data="verify_user"))
    bot.send_message(message.chat.id, "Click below to verify:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "verify_user":
        bot.send_message(call.message.chat.id, "✅ Verified!")

bot.infinity_polling()
