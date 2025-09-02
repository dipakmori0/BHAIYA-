import os, telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN", "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c")
bot = telebot.TeleBot(BOT_TOKEN)

# Channels to check for join
CHANNELS = [-1002851939876, -1002321550721]

# Referral system (simple in-memory)
referrals = {}  # {user_id: referrer_id}
credits = {}    # {user_id: credit_count}

def is_user_joined(user_id):
    for ch_id in CHANNELS:
        try:
            member = bot.get_chat_member(ch_id, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()
    
    # Handle referral
    if len(args) > 1:
        ref_id = int(args[1])
        if user_id not in referrals:
            referrals[user_id] = ref_id
            credits[user_id] = credits.get(user_id, 0) + 3  # New user gets 3
            credits[ref_id] = credits.get(ref_id, 0) + 1  # Referrer gets 1
            bot.send_message(ref_id, f"🎉 Congratulations! Your referral started the bot. +1 credit!")

    if not is_user_joined(user_id):
        text = "❌ You must join our channels first!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 1", url="https://t.me/+eB_J_ExnQT0wZDU9"))
        markup.add(InlineKeyboardButton("Join Channel 2", url="https://t.me/taskblixosint"))
        markup.add(InlineKeyboardButton("Verify", callback_data="verify_join"))
        bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    # VIP Menu
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔍 Vehicle Info", callback_data="vehicle"))
    markup.add(InlineKeyboardButton("👤 Phone Number Lookup", callback_data="phone"))
    markup.add(InlineKeyboardButton("🎁 Referral System", callback_data="referral"))
    markup.add(InlineKeyboardButton("💰 Contact Owner", url="https://t.me/Dex797"))
    bot.send_message(message.chat.id, "🎉 VIP Menu unlocked!\n📌 Choose an option:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "verify_join":
        user_id = call.from_user.id
        if is_user_joined(user_id):
            bot.send_message(call.message.chat.id, "✅ You are verified! Now you can use VIP menu.")
        else:
            bot.answer_callback_query(call.id, "❌ You still haven't joined all channels.")
    elif call.data == "vehicle":
        bot.send_message(call.message.chat.id, "🚗 Vehicle info module coming soon...")
    elif call.data == "phone":
        bot.send_message(call.message.chat.id, "👤 Phone lookup module coming soon...")
    elif call.data == "referral":
        user_id = call.from_user.id
        credit = credits.get(user_id, 0)
        bot.send_message(call.message.chat.id, f"🎁 Your credits: {credit}")

print("🤖 Bot is running...")
bot.infinity_polling()
