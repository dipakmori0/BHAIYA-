import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Get BOT TOKEN from environment or fallback
BOT_TOKEN = os.getenv("BOT_TOKEN", "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c")
bot = telebot.TeleBot(BOT_TOKEN)

print("🤖 Bot starting...")   # for Render logs

# Channels list
CHANNELS = [
    (-1002851939876, "https://t.me/+eB_J_ExnQT0wZDU9"),
    (-1002321550721, "https://t.me/taskblixosint"),
]

# --- Check if user joined channels ---
def is_user_joined(user_id):
    for channel_id, _ in CHANNELS:
        try:
            member = bot.get_chat_member(channel_id, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            print(f"Error checking channel {channel_id}: {e}")
            return False
    return True


# --- Main Menu ---
def main_menu(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📱 Phone Lookup", callback_data="phone"),
        InlineKeyboardButton("🚗 Vehicle Info", callback_data="vehicle"),
    )
    markup.add(
        InlineKeyboardButton("👥 Referral", callback_data="referral"),
    )
    bot.send_message(chat_id, "🎉 Welcome to VIP Main Menu:", reply_markup=markup)


# --- Start Command ---
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    if not is_user_joined(user_id):
        text = "❌ You must join our channels first!"
        markup = InlineKeyboardMarkup()
        for _, link in CHANNELS:
            markup.add(InlineKeyboardButton("Join Channel", url=link))
        markup.add(InlineKeyboardButton("✅ Verify", callback_data="verify"))
        bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    # Already joined
    main_menu(message.chat.id)


# --- Callback Query Handler ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id

    if call.data == "verify":
        if is_user_joined(user_id):
            bot.answer_callback_query(call.id, "✅ Verified!")
            main_menu(call.message.chat.id)
        else:
            bot.answer_callback_query(call.id, "❌ Please join all channels first!")

    elif call.data == "phone":
        bot.send_message(call.message.chat.id, "📱 Enter phone number:")

    elif call.data == "vehicle":
        bot.send_message(call.message.chat.id, "🚗 Enter vehicle number:")

    elif call.data == "referral":
        bot.send_message(call.message.chat.id, "👥 Your referral link will appear here.")


# --- Start Bot ---
bot.infinity_polling(skip_pending=True)
