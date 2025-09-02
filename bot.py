import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN", "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c")
bot = telebot.TeleBot(BOT_TOKEN)

# Channels to join
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
        text = "❌ You must join our channels first!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 1", url="https://t.me/+eB_J_ExnQT0wZDU9"))
        markup.add(InlineKeyboardButton("Join Channel 2", url="https://t.me/taskblixosint"))
        markup.add(InlineKeyboardButton("Verify ✅", callback_data="verify"))
        bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    # VIP welcome message
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Start VIP", callback_data="start_vip"))
    bot.send_message(message.chat.id, "👋 Welcome VIP User!\nClick below to start:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "verify":
        bot.send_message(call.message.chat.id, "✅ Verified! You can now access VIP options.")
    elif call.data == "start_vip":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Vehicle Info 🔍", callback_data="vehicle"))
        markup.add(InlineKeyboardButton("Phone Lookup 👤", callback_data="phone"))
        markup.add(InlineKeyboardButton("Referral 🎁", callback_data="referral"))
        markup.add(InlineKeyboardButton("Contact Owner", url="https://t.me/Dex797"))
        bot.send_message(call.message.chat.id, "🎉 VIP Menu unlocked!\n📌 Choose an option:", reply_markup=markup)

bot.infinity_polling()
