import telebot
import hashlib
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8865908845:AAHuViS1MO3ATppchqLXQZk0zOiNm7cHQK0"
ADMIN_ID = 6866577904
SECRET = "mySuperSecret2026"

bot = telebot.TeleBot(BOT_TOKEN)

# Временное хранилище
user_data = {}  # user_id: {'product': '', 'months': 0, 'total': 0, 'waiting': False}

# Цены
PRICES = {
    'slot': 4,
    'storage': 3,
    'ai': 2,
    'wallpaper': 9
}

# Функция генерации промокода
def generate_key(user_id, product, months=None):
    data = f"{user_id}{product}{months if months else ''}{SECRET}"
    raw_hash = hashlib.md5(data.encode()).hexdigest().upper()[:16]
    return '-'.join([raw_hash[i:i+4] for i in range(0, 16, 4)])

# ===== ПРИВЕТСТВИЕ (список команд) =====
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     f"👋 Привет! Я — магазин для твоего приложения.\n"
                     f"Твой ID: `{message.from_user.id}`\n\n"
                     f"📦 /slot [1-12] — +1 бот к запуску (4₽/мес)\n"
                     f"📁 /storage [1-12] — +1 к хранилищу (3₽/мес)\n"
                     f"🤖 /ai — кастом ИИ (2₽ разово)\n"
                     f"🖼️ /wallpaper [1-12] — кастом обои (9₽/мес)\n\n"
                     f"Пример: `/slot 6` — купить 6 месяцев слота.",
                     parse_mode='Markdown')

# ===== ОБРАБОТКА КОМАНД =====
@bot.message_handler(commands=['slot', 'storage', 'wallpaper'])
def handle_subscription(message):
    product = message.text.split()[0][1:]  # убираем '/'
    try:
        months = int(message.text.split()[1])
        if months < 1 or months > 12:
            raise ValueError
    except:
        bot.reply_to(message, "❌ Укажи число от 1 до 12. Пример: `/slot 6`", parse_mode='Markdown')
        return
    
    user_id = message.from_user.id
    total = PRICES[product] * months
    user_data[user_id] = {'product': product, 'months': months, 'total': total, 'waiting': False}
    
    bot.reply_to(message,
                 f"💰 Товар: {'+1 бот' if product == 'slot' else '+1 хранилище' if product == 'storage' else 'кастом обои'}\n"
                 f"Срок: {months} мес.\n"
                 f"Итого: {total}₽\n\n"
                 f"Переведи на карту: `1234 5678 9012 3456`\n"
                 f"После оплаты напиши мне: `перевел`",
                 parse_mode='Markdown')

@bot.message_handler(commands=['ai'])
def handle_ai(message):
    user_id = message.from_user.id
    user_data[user_id] = {'product': 'ai', 'months': None, 'total': 2, 'waiting': False}
    
    bot.reply_to(message,
                 f"🤖 Кастом ИИ — 2₽ разово\n\n"
                 f"Переведи на карту: `1234 5678 9012 3456`\n"
                 f"После оплаты напиши мне: `перевел`",
                 parse_mode='Markdown')

# ===== ПОЛЬЗОВАТЕЛЬ НАПИСАЛ "ПЕРЕВЕЛ" =====
@bot.message_handler(func=lambda message: message.text.lower() == "перевел")
def paid(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        bot.reply_to(message, "❌ Начни с покупки: `/slot 6` или `/ai`")
        return
    
    user_data[user_id]['waiting'] = True
    bot.send_message(ADMIN_ID,
                     f"🔔 Пользователь {user_id} перевёл деньги!\n"
                     f"Товар: {user_data[user_id]['product']}\n"
                     f"Сумма: {user_data[user_id]['total']}₽\n\n"
                     f"Подтверди: `/Da {user_id}` или отклони: `/Net {user_id}`")
    
    bot.reply_to(message, "⏳ Жди подтверждения от администратора...")

# ===== АДМИН: ПОДТВЕРДИТЬ =====
@bot.message_handler(commands=['Da'])
def da(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split()[1])
    except:
        bot.reply_to(message, "❌ Формат: `/Da 123456`")
        return
    
    if user_id not in user_data:
        bot.reply_to(message, "❌ Пользователь не найден.")
        return
    
    product = user_data[user_id]['product']
    months = user_data[user_id].get('months', None)
    promo = generate_key(user_id, product, months)
    
    bot.send_message(user_id, f"🎉 Платёж подтверждён! Твой промокод:\n`{promo}`\n\nВведи его в приложении.")
    bot.reply_to(message, f"✅ Промокод для {user_id} отправлен.")
    del user_data[user_id]

# ===== АДМИН: ОТКЛОНИТЬ =====
@bot.message_handler(commands=['Net'])
def net(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split()[1])
    except:
        bot.reply_to(message, "❌ Формат: `/Net 123456`")
        return
    
    if user_id in user_data:
        bot.send_message(user_id, "❌ Платёж не подтверждён. Проверь реквизиты и попробуй снова через 1 час.")
        bot.reply_to(message, f"❌ Платёж от {user_id} отклонён.")
        del user_data[user_id]
    else:
        bot.reply_to(message, "❌ Пользователь не найден.")

# ===== ГЕНЕРАЦИЯ КЛЮЧА ВРУЧНУЮ (для админа) =====
@bot.message_handler(commands=['genkey'])
def genkey(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Формат: `/genkey user_id product` (product: slot/storage/ai/wallpaper)")
        return
    _, uid, prod = parts
    key = generate_key(int(uid), prod, 1)
    bot.reply_to(message, f"Ключ: `{key}`", parse_mode='Markdown')

print("Бот с командами запущен!")
bot.infinity_polling()
