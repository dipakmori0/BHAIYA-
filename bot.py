import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔑 Bot token (Render ke "Environment Variables" me bhi add karo: BOT_TOKEN)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c")
bot = telebot.TeleBot(BOT_TOKEN)

print("🤖 Bot starting...")   # Render logs me turant dikhne ke liye

# 🔹 Channels IDs
CHANNELS = [-1002851939876, -1002321550721]

# ✅ User joined check function
def is_user_joined(user_id):
    for channel_id in CHANNELS:
        try:
            member = bot.get_chat_member(channel_id, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

# 🔹 Start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    print(f"📩 /start from {user_id}")

    if not is_user_joined(user_id):
        text = "❌ You must join our channels first!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 1", url="https://t.me/+eB_J_ExnQT0wZDU9"))
        markup.add(InlineKeyboardButton("Join Channel 2", url="https://t.me/taskblixosint"))
        markup.add(InlineKeyboardButton("✅ Verify", callback_data="verify"))
        bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    # Agar joined hai
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Start VIP", callback_data="start_vip"))
    bot.send_message(message.chat.id, "👋 Welcome VIP User!\nClick below to start:", reply_markup=markup)

# 🔹 Callback handling
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id

    if call.data == "verify":
        if is_user_joined(user_id):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🚀 Start VIP", callback_data="start_vip"))
            bot.edit_message_text(
                "✅ Verification successful!\nWelcome VIP User!",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        else:
            bot.answer_callback_query(call.id, "❌ Please join all channels first.")

    elif call.data == "start_vip":
        bot.send_message(call.message.chat.id, "🎉 VIP Menu unlocked!\n\n📌 Options:\n1. 🔍 Vehicle Info\n2. 👤 Phone Number Lookup\n3. 🎁 Referral System")

# 🔄 Keep polling
bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
