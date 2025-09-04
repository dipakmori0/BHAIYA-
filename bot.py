import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import sqlite3
import requests
import time
from flask import Flask, request

# ---------------- CONFIG ----------------
BOT_TOKEN = "8304954508:AAHLxY3YfPHwF1dnBxv8noLUhmz9YxV5MxU"
API_TOKEN = "7658050410:WJ8iTpuZ"
PEOPLE_API_URL = "https://leakosintapi.com/"
VEHICLE_API_URL = "https://vehicleinfo.zerovault.workers.dev/?VIN="

BOT_USERNAME = "rajputteam_bot"
OWNER_USERNAME = "@CodeWraiithHere"

CHANNELS = [
    {"link": "https://t.me/+eB_J_ExnQT0wZDU9", "id": "-1002851939876"},
    {"link": "https://t.me/taskblixosint", "id": "-1002851939876"},
    {"link": "https://t.me/CHOMUDONKIMAKICHUT", "id": "-1002921007541"}
]

UNLIMITED_USERS = []
REDEEM_CODES = {"FREE5": 5, "BONUS10": 10}  # Example redeem codes

# ---------- DATABASE ----------
conn = sqlite3.connect('users.db', check_same_thread=False)

def execute_db(query, params=(), fetch=False):
    cur = conn.cursor()
    cur.execute(query, params)
    result = cur.fetchone() if fetch else None
    conn.commit()
    cur.close()
    return result

execute_db('''CREATE TABLE IF NOT EXISTS users (
user_id TEXT PRIMARY KEY,
credits INTEGER DEFAULT 3,
ref_by TEXT
)''')

def add_user(user_id, ref_by=None):
    execute_db("INSERT OR IGNORE INTO users (user_id, credits, ref_by) VALUES (?, ?, ?)",
               (str(user_id), 3, ref_by))

def use_credit(user_id):
    if user_id in UNLIMITED_USERS: return True
    row = execute_db("SELECT credits FROM users WHERE user_id=?", (str(user_id),), fetch=True)
    if row and row[0] > 0:
        execute_db("UPDATE users SET credits=credits-1 WHERE user_id=?", (str(user_id),))
        return True
    return False

def add_credits(user_id, amount):
    execute_db("UPDATE users SET credits=credits+? WHERE user_id=?", (amount, str(user_id)))

def get_credits(user_id):
    if user_id in UNLIMITED_USERS: return "Unlimited"
    row = execute_db("SELECT credits FROM users WHERE user_id=?", (str(user_id),), fetch=True)
    return row[0] if row else 0

def add_referral(ref_user_id):
    add_credits(ref_user_id, 1)

def get_referral_link(user_id):
    return f"https://t.me/{BOT_USERNAME}?start=REF{user_id}"

# ---------- API FUNCTIONS ----------
def generate_people_report(phone):
    data = {"token": API_TOKEN, "request": phone, "limit": 300, "lang": "en"}
    try:
        response = requests.post(PEOPLE_API_URL, json=data, timeout=15).json()
    except:
        return "❌ API returned invalid response"
    if "Error code" in response:
        return "❌ No results found"
    result_texts = []
    for db_name in response.get("List", {}):
        db_result = response["List"][db_name]
        for record in db_result.get("Data", []):
            lines = []
            if "FullName" in record: lines.append(f"🧑 Name: {record['FullName']}")
            if "FatherName" in record: lines.append(f"👨 Father's Name: {record['FatherName']}")
            if "DocNumber" in record: lines.append(f"🆔 Document Number: {record['DocNumber']}")
            if "Region" in record: lines.append(f"📍 Region: {record['Region']}")
            if "Address" in record: lines.append(f"🏠 Address: {record['Address']}")
            phone_list = [v for k, v in record.items() if k.startswith("Phone")]
            if phone_list:
                phone_lines = "\n".join([f"  {i+1}️⃣ {p}" for i, p in enumerate(phone_list)])
                lines.append(f"📞 Phones:\n{phone_lines}")
            result_texts.append("\n".join(lines))
    if not result_texts:
        return "❌ No results found"
    return "\n\n".join(result_texts)

def generate_vehicle_report(vin):
    try:
        response = requests.get(VEHICLE_API_URL + vin, timeout=15).json()
        if "error" in response:
            return f"❌ Vehicle info not found for VIN: {vin}"
        lines = ["🚗 VEHICLE INFORMATION"]
        for k, v in response.items():
            if isinstance(v, bool): v = "✅" if v else "❌"
            lines.append(f"{k.replace('_',' ').title()}: {v}")
        return "\n".join(lines)
    except:
        return f"❌ Failed to fetch vehicle info for VIN: {vin}"

# ---------- BOT ----------
bot = telebot.TeleBot(BOT_TOKEN)

def check_joined(user_id):
    # Placeholder for real join check
    return True

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    ref_by = None
    if message.text.startswith("/start REF"):
        ref_by = message.text.split("REF")[1]
        add_referral(ref_by)
        bot.send_message(user_id, "🎉 You got 1 credit for referral!")
    add_user(user_id, ref_by)

    markup = InlineKeyboardMarkup(row_width=1)
    for i, ch in enumerate(CHANNELS, 1):
        markup.add(InlineKeyboardButton(f"Join Channel {i}", url=ch['link']))
    markup.add(InlineKeyboardButton("✅ Verify Joined Channels", callback_data="verify_all"))
    bot.send_message(user_id, "⚠️ Please join all channels first and verify:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    user_id = call.from_user.id
    if call.data == "verify_all":
        if check_joined(user_id):
            bot.send_message(user_id, "✅ Verified! Starting bot...")
            show_main_menu(user_id)
        else:
            bot.answer_callback_query(call.id, "❌ You are not a member of all channels yet!")
    elif call.data == "number":
        msg = bot.send_message(user_id, "📞 Enter phone number with country code (e.g., 919XXXXXXXXX):")
        bot.register_next_step_handler(msg, process_number)
    elif call.data == "vehicle":
        msg = bot.send_message(user_id, "🚗 Enter vehicle VIN or number:")
        bot.register_next_step_handler(msg, process_vehicle)
    elif call.data == "balance":
        bot.send_message(user_id, f"💳 Your credits: {get_credits(user_id)}")
    elif call.data == "referral":
        bot.send_message(user_id, f"🔗 Your referral link:\n{get_referral_link(user_id)}")
    elif call.data == "redeem":
        msg = bot.send_message(user_id, "💰 Enter redeem code:")
        bot.register_next_step_handler(msg, process_redeem)

def show_main_menu(user_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📞 Number Info", callback_data="number"),
        InlineKeyboardButton("🚗 Vehicle Info", callback_data="vehicle"),
        InlineKeyboardButton("💳 Check Balance", callback_data="balance"),
        InlineKeyboardButton("🔗 Referral", callback_data="referral"),
        InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem")
    )
    bot.send_message(user_id, "👋 Welcome! Select an option:", reply_markup=markup)

def hacker_animation(user_id, target):
    bar = ""
    for i in range(10):
        bar += "▓"
        bot.send_message(user_id, f"🚀 {target} [{bar}{'░'*(10-i-1)}]")
        time.sleep(0.4)

def process_number(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    hacker_animation(user_id, phone)
    if use_credit(user_id):
        result = generate_people_report(phone)
        bot.send_message(user_id, result)
    else:
        bot.send_message(user_id, "❌ Not enough credits.")
    show_main_menu(user_id)

def process_vehicle(message):
    user_id = message.from_user.id
    vin = message.text.strip()
    hacker_animation(user_id, vin)
    if use_credit(user_id):
        result = generate_vehicle_report(vin)
        bot.send_message(user_id, result)
    else:
        bot.send_message(user_id, "❌ Not enough credits.")
    show_main_menu(user_id)

def process_redeem(message):
    user_id = message.from_user.id
    code = message.text.strip().upper()
    if code in REDEEM_CODES:
        add_credits(user_id, REDEEM_CODES[code])
        bot.send_message(user_id, f"🎉 Code applied! You got {REDEEM_CODES[code]} credits.")
    else:
        bot.send_message(user_id, "❌ Invalid redeem code.")
    show_main_menu(user_id)

# ---------- WEBHOOK MODE ----------
app = Flask(__name__)

@app.route("/" + BOT_TOKEN, methods=["POST"])
def getMessage():
    json_str = request.stream.read().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def webhook():
    return "🤖 Bot is running", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://BHAIYA-1.onrender.com/{BOT_TOKEN}")  # apna Render URL lagao
    app.run(host="0.0.0.0", port=port)
