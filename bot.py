import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c"
bot = telebot.TeleBot(BOT_TOKEN)

# Channels
CHANNELS = [
    {"id": -1002851939876, "url": "https://t.me/+eB_J_ExnQT0wZDU9"},
    {"id": -1002321550721, "url": "https://t.me/taskblixosint"}
]

def is_user_joined(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel["id"], user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    markup = InlineKeyboardMarkup()
    
    # Channel join buttons
    for channel in CHANNELS:
        markup.add(InlineKeyboardButton(f"Join {channel['url'].split('/')[-1]}", url=channel["url"]))

    # Verify button (always below join buttons)
    markup.add(InlineKeyboardButton("✅ Verify", callback_data="verify"))

    if not is_user_joined(user_id):
        bot.send_message(message.chat.id, "❌ You must join our channels first!", reply_markup=markup)
        return

    # VIP welcome message if joined
    bot.send_message(message.chat.id, "👋 Welcome VIP User!\nClick below to verify:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "verify":
        user_id = call.from_user.id
        if is_user_joined(user_id):
            bot.send_message(call.message.chat.id, "🎉 Verified! You can now access VIP features.")
        else:
            bot.send_message(call.message.chat.id, "❌ You must join all channels before verification!")

bot.infinity_polling()
