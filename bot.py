import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import sqlite3
import requests

# ---------------- CONFIG ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c"
API_TOKEN = os.getenv("API_TOKEN") or "7658050410:qQ88TxXl"
PEOPLE_API_URL = "https://leakosintapi.com/"
VEHICLE_API_URL = "https://vehicleinfo.zerovault.workers.dev/?VIN="

CHANNELS = {
    -1002851939876: "https://t.me/+eB_J_ExnQT0wZDU9",
    -1002321550721: "https://t.me/taskblixosint"
}

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            credits INTEGER DEFAULT 0,
            ref_by TEXT
        )
    """)
    conn.commit()
    conn.close()

def execute_db(query, params=(), fetch=False):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute(query, params)
    data = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# ---------- USERS ----------
def add_user(user_id, ref_by=None):
    row = execute_db("SELECT * FROM users WHERE user_id=?", (str(user_id),), fetch=True)
    if row:
        return False

    execute_db("INSERT INTO users (user_id, credits, ref_by) VALUES (?, ?, ?)", (str(user_id), 3, ref_by))

    if ref_by:
        execute_db("UPDATE users SET credits = credits + 1 WHERE user_id=?", (str(ref_by),))
        try:
            bot.send_message(ref_by, "🎉 Congratulations! You earned 1 credit for referral.")
        except:
            pass
    return True

def get_credits(user_id):
    row = execute_db("SELECT credits FROM users WHERE user_id=?", (str(user_id),), fetch=True)
    return row[0][0] if row else 0

def use_credit(user_id):
    row = execute_db("SELECT credits FROM users WHERE user_id=?", (str(user_id),), fetch=True)
    if not row or row[0][0] <= 0:
        return False
    execute_db("UPDATE users SET credits = credits - 1 WHERE user_id=?", (str(user_id),))
    return True

# ---------- JOIN CHECK ----------
def check_joined(user_id):
    for channel_id in CHANNELS.keys():
        try:
            member = bot.get_chat_member(channel_id, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# ---------- MAIN MENU ----------
def show_main_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("👤 Phone Info", callback_data="phone"))
    markup.add(InlineKeyboardButton("🚗 Vehicle Info", callback_data="vehicle"))
    markup.add(InlineKeyboardButton("💰 Your Credits", callback_data="balance"))
    markup.add(InlineKeyboardButton("🔗 Referral Link", callback_data="referral"))
    bot.send_message(user_id, "📌 Choose an option:", reply_markup=markup)

# ---------- PHONE API ----------
def handle_phone(user_id, number):
    if not use_credit(user_id):
        bot.send_message(user_id, "❌ No credits left!")
        return

    msg = bot.send_message(user_id, f"📞 Processing number info for {number}...\n⏳ Please wait...")

    try:
        payload = {"token": API_TOKEN, "request": number, "limit": 300, "lang": "en"}
        res = requests.post(PEOPLE_API_URL, json=payload, timeout=15).json()

        if not res.get("List"):
            bot.edit_message_text("❌ Phone info not found for this number.", user_id, msg.message_id)
            return

        results = []
        for db_name in res.get("List", {}):
            for record in res["List"][db_name].get("Data", []):
                lines = [
                    f"🧑 Name: {record.get('FullName', '-')}",
                    f"👨 Father's Name: {record.get('FatherName', '-')}",
                    f"🆔 Document Number: {record.get('DocNumber', '-')}",
                    f"📍 Region: {record.get('Region', '-')}",
                    f"🏠 Address: {record.get('Address', '-')}"
                ]
                phone_list = [v for k,v in record.items() if k.startswith("Phone")]
                if phone_list:
                    lines.append("📞 Phones:\n" + "\n".join([f"  {i+1}️⃣ {p}" for i,p in enumerate(phone_list)]))
                results.append("\n".join(lines))

        bot.edit_message_text("👤 Phone info:\n\n" + "\n\n".join(results), user_id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"⚠️ Phone API error!\n{str(e)}", user_id, msg.message_id)

# ---------- VEHICLE API ----------
def handle_vehicle(user_id, vin):
    if not use_credit(user_id):
        bot.send_message(user_id, "❌ No credits left!")
        return

    msg = bot.send_message(user_id, f"🚗 Processing vehicle info for {vin}...\n⏳ Please wait...")

    try:
        res = requests.get(VEHICLE_API_URL + vin, timeout=15).json()
        if "error" in res:
            bot.edit_message_text(f"❌ Vehicle info not found for VIN: {vin}", user_id, msg.message_id)
            return

        lines = ["🚗 VEHICLE INFORMATION"]
        for k,v in res.items():
            if isinstance(v, bool): v = "✅" if v else "❌"
            lines.append(f"{k.replace('_',' ').title()}: {v}")
        bot.edit_message_text("\n".join(lines), user_id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"⚠️ Vehicle API error!\n{str(e)}", user_id, msg.message_id)

# ---------- BOT ----------
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)
    ref_by = None

    if message.text.startswith("/start REF"):
        ref_by = message.text.split("REF")[1]
        if ref_by == user_id:
            ref_by = None

    is_new = add_user(user_id, ref_by)

    if not check_joined(user_id):
        markup = InlineKeyboardMarkup()
        for link in CHANNELS.values():
            markup.add(InlineKeyboardButton("Join Channel", url=link))
        markup.add(InlineKeyboardButton("✅ Continue", callback_data="continue"))
        bot.send_message(user_id, "⚠️ Please join our channels first:", reply_markup=markup)
        return

    if is_new:
        bot.send_message(user_id, "👋 Welcome! You got 3 free credits 🎁")

    show_main_menu(user_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    user_id = str(call.from_user.id)

    if call.data == "continue":
        if check_joined(user_id):
            show_main_menu(user_id)
        else:
            bot.answer_callback_query(call.id, "⚠️ Please join all channels!")

    elif call.data == "phone":
        msg = bot.send_message(user_id, "👤 Enter phone number with country code:")
        bot.register_next_step_handler(msg, lambda m: handle_phone(user_id, m.text))

    elif call.data == "vehicle":
        msg = bot.send_message(user_id, "🚗 Enter vehicle VIN/Number:")
        bot.register_next_step_handler(msg, lambda m: handle_vehicle(user_id, m.text))

    elif call.data == "balance":
        credits = get_credits(user_id)
        bot.send_message(user_id, f"💰 Your Credits: {credits}")

    elif call.data == "referral":
        ref_link = f"https://t.me/{bot.get_me().username}?start=REF{user_id}"
        bot.send_message(user_id, f"🔗 Share this referral link:\n{ref_link}\n\n🎁 New users get 3 credits, you earn 1 credit per referral!")

# ---------- START BOT ----------
if __name__ == "__main__":
    init_db()
    print("🤖 Bot is running...")
    bot.infinity_polling()
