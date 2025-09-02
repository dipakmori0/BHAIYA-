import telebot
from telebot import types

# ✅ Tumhara bot token
API_TOKEN = "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c"

# Channels with IDs and invite links
CHANNELS = [
    {"id": -1002851939876, "link": "https://t.me/+eB_J_ExnQT0wZDU9", "name": "Channel 1"},
    {"id": -1002321550721, "link": "https://t.me/taskblixosint", "name": "Channel 2"}
]

bot = telebot.TeleBot(API_TOKEN)

def is_user_in_channels(user_id):
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch["id"], user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

def channel_join_markup():
    markup = types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        markup.add(types.InlineKeyboardButton(
            text=f"Join {ch['name']}",
            url=ch['link']  # Direct join link
        ))
    markup.add(types.InlineKeyboardButton(text="✅ Verify", callback_data="verify"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not is_user_in_channels(user_id):
        bot.send_message(message.chat.id, "❌ Please join the required channel(s) first!", reply_markup=channel_join_markup())
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🚀 Start"))
        bot.send_message(message.chat.id, "👋 Welcome VIP User!\nClick below to start:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    user_id = call.from_user.id
    if is_user_in_channels(user_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🚀 Start"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="✅ Verified! Welcome VIP User!\nClick below to start:", reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "❌ You are not yet joined in all required channels!", show_alert=True)

bot.infinity_polling()
