import telebot
import hashlib
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8865908845:AAHuViS1MO3ATppchqLXQZk0zOiNm7cHQK0"  # ТОТ ЖЕ ТОКЕН (без опечаток)
ADMIN_ID = 6866577904  # ТВОЙ НАСТОЯЩИЙ ID (не 686577904)
SECRET = "mySuperSecret2026"  # можешь оставить

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

def generate_key(user_id, product, months):
    # Правильная формула (без лишних скобок)
    data = f"{user_id}{product}{months}{SECRET}"
    raw_hash = hashlib.md5(data.encode()).hexdigest().upper()[:16]  # первые 16 символов
    return '-'.join([raw_hash[i:i+4] for i in range(0, 16, 4)])

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_data[user_id] = True
    bot.reply_to(message, f"👋 Привет! Твой ID: `{user_id}`", parse_mode='Markdown')

@bot.message_handler(commands=['buy_pro'])
def buy_pro(message):
    user_id = message.from_user.id
    promo = generate_key(user_id, 'pro', 1)
    bot.reply_to(message, f"💰 Промокод: `{promo}`\nОплати 19₽ и введи в приложении.", parse_mode='Markdown')

@bot.message_handler(commands=['genkey'])
def genkey(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) != 4:
        bot.reply_to(message, "Формат: /genkey user_id product months")
        return
    _, uid, prod, mon = parts
    key = generate_key(int(uid), prod, int(mon))
    bot.reply_to(message, f"Ключ: `{key}`", parse_mode='Markdown')

print("Бот запущен!")
bot.infinity_polling()
