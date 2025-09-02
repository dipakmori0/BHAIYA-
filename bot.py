import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot token
BOT_TOKEN = "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c"
bot = telebot.TeleBot(BOT_TOKEN)

# Channels to verify
CHANNELS = [
    {"id": -1002851939876, "url": "https://t.me/+eB_J_ExnQT0wZDU9", "name": "Channel 1"},
    {"id": -1002321550721, "url": "https://t.me/taskblixosint", "name": "Channel 2"}
]

def is_user_joined(user_id):
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch["id"], user_id)
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
        for ch in CHANNELS:
            markup.add(InlineKeyboardButton(f"Join {ch['name']}", url=ch["url"]))
        # Verify button below channels
        markup.add(InlineKeyboardButton("✅ Verify", callback_data="verify"))
        bot.send_message(message.chat.id, "❌ You must join our channels first!", reply_markup=markup)
        return

    # VIP welcome message
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Start VIP", callback_data="start_vip"))
    bot.send_message(message.chat.id, "👋 Welcome VIP User!\nClick below to start:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id

    if call.data == "verify":
        if is_user_joined(user_id):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Start VIP", callback_data="start_vip"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="✅ You are verified! Click below to start:", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "❌ You still need to join all channels.", show_alert=True)

    elif call.data == "start_vip":
        bot.send_message(call.message.chat.id, "🎉 VIP options unlocked! You can now access all features.")
        # Add more VIP buttons or features here

bot.infinity_polling()
