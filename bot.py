import requests
import sqlite3
from random import randint
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------------- CONFIG ----------------
BOT_TOKEN = "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c"
API_TOKEN = "7658050410:qQ88TxXl"
PEOPLE_API_URL = "https://leakosintapi.com/"
VEHICLE_API_URL = "https://vehicleinfo.zerovault.workers.dev/"
BOT_USERNAME = "Hahwjahjjahabot"
OWNER_USERNAME = "@CodeWraiithHere"

CHANNELS = [
    {"id": -1002851939876, "link": "https://t.me/+pZ17mKu0yZYwYmVl"},
    {"id": -1002321550721, "link": "https://t.me/taskblixosint"}
]

UNLIMITED_USERS = [5145179256, 8270660057]

# ---------- DATABASE ----------
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    credit INTEGER DEFAULT 3,
    referrer TEXT
)""")
conn.commit()

# ---------- BOT ----------
bot = telebot.TeleBot(BOT_TOKEN)

# ---------- HELPERS ----------
def is_user_joined(user_id):
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch["id"], user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

def get_user_credit(user_id):
    cursor.execute("SELECT credit FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute("INSERT INTO users(user_id) VALUES (?)", (user_id,))
    conn.commit()
    return 3

def update_user_credit(user_id, amount):
    credit = get_user_credit(user_id) + amount
    cursor.execute("UPDATE users SET credit=? WHERE user_id=?", (credit, user_id))
    conn.commit()

# ---------- API CALLS ----------
def fetch_vehicle_info(rid):
    try:
        resp = requests.get(f"{VEHICLE_API_URL}?rid={rid}&token={API_TOKEN}").json()
        return resp
    except:
        return {"message": "Vehicle API error"}

def fetch_phone_info(phone):
    try:
        resp = requests.get(f"{PEOPLE_API_URL}?phone={phone}&token={API_TOKEN}").json()
        return resp
    except:
        return {"message": "Phone API error"}

# ---------- HANDLERS ----------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    # Channels join check
    if not is_user_joined(user_id):
        markup = InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(InlineKeyboardButton(f"Join Channel", url=ch["link"]))
        bot.send_message(message.chat.id, "❌ You must join our channels first!", reply_markup=markup)
        return

    # VIP welcome
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Vehicle Info", callback_data="vehicle"))
    markup.add(InlineKeyboardButton("Phone Lookup", callback_data="phone"))
    markup.add(InlineKeyboardButton("Referral System", callback_data="referral"))
    bot.send_message(message.chat.id, "👋 Welcome VIP User!\nSelect an option:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id

    if call.data == "vehicle":
        msg = bot.send_message(call.message.chat.id, "🚗 Enter RID:")
        bot.register_next_step_handler(msg, handle_vehicle)

    elif call.data == "phone":
        msg = bot.send_message(call.message.chat.id, "👤 Enter phone number with country code:")
        bot.register_next_step_handler(msg, handle_phone)

    elif call.data == "referral":
        credit = get_user_credit(user_id)
        bot.send_message(call.message.chat.id, f"🎁 Your current credit: {credit}\nShare your link: t.me/{BOT_USERNAME}?start={user_id}")

def handle_vehicle(message):
    rid = message.text
    info = fetch_vehicle_info(rid)
    bot.send_message(message.chat.id, f"🚗 Vehicle Info:\n{info}")

def handle_phone(message):
    phone = message.text
    info = fetch_phone_info(phone)
    bot.send_message(message.chat.id, f"👤 Phone Info:\n{info}")

# ---------- RUN ----------
print("🤖 Bot started...")
bot.infinity_polling()
