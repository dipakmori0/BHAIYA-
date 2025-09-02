import os, telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ====== BOT TOKEN ======
BOT_TOKEN = "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c"   # << अपना token यहाँ
bot = telebot.TeleBot(BOT_TOKEN)

# ====== SETTINGS ======
CHANNELS = ["@YourChannelHere"]  # यहाँ अपना चैनल username डाल
SIGNUP_BONUS = 3
REFERRAL_BONUS = 1

# ====== DATABASE (memory only) ======
user_balance = {}
user_referrals = {}

# ====== BALANCE SYSTEM ======
def get_balance(user_id):
    return user_balance.get(user_id, 0)

def add_balance(user_id, amount):
    user_balance[user_id] = get_balance(user_id) + amount

# ====== CHECK CHANNEL JOIN ======
def check_subscription(user_id):
    # अभी demo में हमेशा True
    # असली check करने के लिए Telegram API का इस्तेमाल करना पड़ेगा
    return True

# ====== START COMMAND ======
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.chat.id
    parts = message.text.split()

    # नया user bonus
    if user_id not in user_balance:
        add_balance(user_id, SIGNUP_BONUS)
        bot.send_message(
            user_id,
            f"🎁 Welcome! You got {SIGNUP_BONUS} free credits.\n💰 Balance: {get_balance(user_id)}"
        )

    # referral check
    if len(parts) > 1:
        referrer_id = parts[1]
        if referrer_id.isdigit() and int(referrer_id) != user_id:
            referrer_id = int(referrer_id)
            if referrer_id not in user_referrals:
                user_referrals[referrer_id] = []
            if user_id not in user_referrals[referrer_id]:
                user_referrals[referrer_id].append(user_id)
                add_balance(referrer_id, REFERRAL_BONUS)

                # 🎉 Referrer को msg
                bot.send_message(
                    referrer_id,
                    f"🎉 Congratulations!\nSomeone joined with your link.\n💰 +{REFERRAL_BONUS} credit\nBalance: {get_balance(referrer_id)}"
                )

    # channel verify
    if not check_subscription(user_id):
        markup = InlineKeyboardMarkup()
        for channel in CHANNELS:
            markup.add(InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{channel.replace('@','')}"))
        markup.add(InlineKeyboardButton("✅ Verify", callback_data="verify"))
        bot.send_message(user_id, "❌ You must join our channels first!", reply_markup=markup)
    else:
        show_menu(user_id)

# ====== MENU ======
def show_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚘 Vehicle Info", callback_data="vehicle"))
    markup.add(InlineKeyboardButton("📱 Phone Number Lookup", callback_data="phone"))
    markup.add(InlineKeyboardButton("🎁 Referral System", callback_data="referral"))
    markup.add(InlineKeyboardButton("👤 Contact Owner", url="https://t.me/Dex797"))  # यहाँ Owner username
    bot.send_message(user_id, "🎉 VIP Menu unlocked!\n\n📌 Choose an option:", reply_markup=markup)

# ====== BALANCE COMMAND ======
@bot.message_handler(commands=["balance"])
def balance_cmd(message):
    user_id = message.chat.id
    bot.send_message(user_id, f"💰 Your Balance: {get_balance(user_id)} credits")

print("🤖 Bot is running...")
bot.infinity_polling()
