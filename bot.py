import os, telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN", "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c")
bot = telebot.TeleBot(BOT_TOKEN)

# ---- Channel IDs ----
CHANNELS = ["@YourChannel1", "@YourChannel2"]

print("🤖 Bot starting...")   # logs me dikhega

# ✅ Function: check user joined
def is_member(user_id):
    try:
        for ch in CHANNELS:
            chat_member = bot.get_chat_member(ch, user_id)
            if chat_member.status in ["left", "kicked"]:
                return False
        return True
    except Exception as e:
        print("Check member error:", e)
        return False

# ✅ Start Command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if not is_member(user_id):
        markup = InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(InlineKeyboardButton(f"Join {ch}", url=f"https://t.me/{ch[1:]}"))
        markup.add(InlineKeyboardButton("✅ Verify", callback_data="verify"))
        bot.reply_to(message, "❌ You must join our channels first!", reply_markup=markup)
    else:
        show_menu(message.chat.id)

# ✅ Verify Button
@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    if is_member(call.from_user.id):
        show_menu(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "❌ Please join all channels first!")

# ✅ Menu Function
def show_menu(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📱 Phone Lookup", callback_data="phone"))
    markup.add(InlineKeyboardButton("🚗 Vehicle Info", callback_data="vehicle"))
    markup.add(InlineKeyboardButton("👥 Referral", callback_data="referral"))
    bot.send_message(chat_id, "👋 Welcome VIP User!\nChoose an option:", reply_markup=markup)

# ✅ Polling Loop
bot.remove_webhook()
bot.infinity_polling(timeout=60, long_polling_timeout=30)
