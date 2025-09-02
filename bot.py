import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# === Bot Token ===
BOT_TOKEN = "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c"
bot = telebot.TeleBot(BOT_TOKEN)

# === Channels IDs ===
CHANNELS = [-1002851939876, -1002321550721]

# === Check if user joined all channels ===
def is_user_joined(user_id):
    for channel_id in CHANNELS:
        try:
            member = bot.get_chat_member(channel_id, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

# === Start command ===
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if not is_user_joined(user_id):
        # Channels join buttons
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 1", url="https://t.me/+eB_J_ExnQT0wZDU9"))
        markup.add(InlineKeyboardButton("Join Channel 2", url="https://t.me/taskblixosint"))
        # Verify button below join
        markup.add(InlineKeyboardButton("✅ Verify", callback_data="verify"))
        bot.send_message(message.chat.id, "❌ You must join our channels first!", reply_markup=markup)
        return

    # VIP welcome message with main menu
    main_menu(message.chat.id)

# === Main menu function ===
def main_menu(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚗 Vehicle Info", callback_data="vehicle"))
    markup.add(InlineKeyboardButton("📞 Phone Number", callback_data="phone"))
    markup.add(InlineKeyboardButton("🎁 Referral", callback_data="referral"))
    bot.send_message(chat_id, "👋 Welcome VIP User!\nSelect an option below:", reply_markup=markup)

# === Callback handler ===
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id

    if call.data == "verify":
        if is_user_joined(user_id):
            bot.send_message(call.message.chat.id, "✅ Verified! All options unlocked.")
            main_menu(call.message.chat.id)
        else:
            bot.send_message(call.message.chat.id, "❌ You still need to join all channels first!")
    
    elif call.data == "vehicle":
        bot.send_message(call.message.chat.id, "🚗 Processing vehicle info...\n⏳ Please wait...")
        # Vehicle info logic here
        bot.send_message(call.message.chat.id, "🚗 VEHICLE INFORMATION\nMessage: Vehicle details not found.\nCode: 1018")

    elif call.data == "phone":
        bot.send_message(call.message.chat.id, "📞 Your phone number info will appear here.")

    elif call.data == "referral":
        bot.send_message(call.message.chat.id, "🎁 Your referral info will appear here.")

# === Start the bot ===
bot.infinity_polling()
