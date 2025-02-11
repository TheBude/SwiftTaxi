import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import logging

TOKEN = "8107721381:AAFopJe7xPz1fUrD7Fw6C7EJm64vQl_Fhes"
bot = telebot.TeleBot(TOKEN)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

user_data = {}
user_messages = {}

def delete_previous_message(chat_id):
    if chat_id in user_messages:
        try:
            bot.delete_message(chat_id, user_messages[chat_id])
        except:
            pass

def send_message(chat_id, text, reply_markup=None):
    delete_previous_message(chat_id)
    msg = bot.send_message(chat_id, text, reply_markup=reply_markup)
    user_messages[chat_id] = msg.message_id

def send_callback_message(call, text, reply_markup=None):
    chat_id = call.message.chat.id
    delete_previous_message(chat_id)
    msg = bot.send_message(chat_id, text, reply_markup=reply_markup)
    user_messages[chat_id] = msg.message_id

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    text = "👋 Assalomu alaykum, SwiftCab botiga xush kelibsiz!\n\n" \
           "🚖 Sizga tezkor va qulay taksi xizmatini taklif qilamiz!\n\n" \
           "📍 Yo‘nalishingizni tanlang:"

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("🚖 Yo'lovchi", callback_data='passenger'),
               InlineKeyboardButton("🚕 Haydovchi", callback_data='driver'))

    send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'driver')
def driver_info(call):
    chat_id = call.message.chat.id
    text = "🚕 Hurmatli haydovchi, bizning kanalga o'tib, o'zingizga mos klient topishingiz mumkin!"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 Kanalga o'tish", url="https://t.me/SwiftCabuz"))
    send_callback_message(call, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'passenger')
def ask_name(call):
    chat_id = call.message.chat.id
    user_data[chat_id] = {'role': 'passenger'}
    send_callback_message(call, "✍️ Ismingizni kiriting:")
    bot.register_next_step_handler_by_chat_id(chat_id, ask_phone)

def ask_phone(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text
    send_message(chat_id, "📞 Telefon raqamingizni yuboring (+998xxxxxxxxx):")
    bot.register_next_step_handler_by_chat_id(chat_id, check_phone)

def check_phone(message):
    chat_id = message.chat.id
    phone = message.text

    if phone.startswith('+998') and phone[1:].isdigit() and len(phone) == 13:
        user_data[chat_id]['phone'] = phone
        ask_route(message)
    else:
        send_message(chat_id, "❌ Raqamingiz noto‘g‘ri. Iltimos, +998 bilan boshlanuvchi to‘g‘ri raqam kiriting!")
        bot.register_next_step_handler_by_chat_id(chat_id, check_phone)

def ask_route(message):
    chat_id = message.chat.id
    text = "📍 Yo‘nalishingizni tanlang:"
    markup = InlineKeyboardMarkup()
    routes = ["Toshkent-Samarqand", "Samarqand-Toshkent", "Sazagan-Seliskiy", "Seliskiy-Sazagan", "Sazagan-Nurobod",
              "Nurobod-Sazagan"]

    for route in routes:
        markup.add(InlineKeyboardButton(route, callback_data=f'route_{route}'))

    send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('route_'))
def ask_passengers(call):
    chat_id = call.message.chat.id
    user_data[chat_id]['route'] = call.data.replace('route_', '')

    text = "🧑‍🤝‍🧑 Yo‘lovchilar sonini tanlang:"
    markup = InlineKeyboardMarkup()
    for i in range(1, 5):
        markup.add(InlineKeyboardButton(f"{i} ta", callback_data=f'passengers_{i}'))

    send_callback_message(call, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('passengers_'))
def confirm_data(call):
    chat_id = call.message.chat.id
    user_data[chat_id]['passengers'] = call.data.replace('passengers_', '')

    text = (f"✅ Ma'lumotlaringiz:\n\n"
            f"👤 Ism: {user_data[chat_id]['name']}\n"
            f"📞 Telefon: {user_data[chat_id]['phone']}\n"
            f"📍 Yo‘nalish: {user_data[chat_id]['route']}\n"
            f"🧑‍🤝‍🧑 Yo‘lovchilar: {user_data[chat_id]['passengers']} ta\n\n"
            "Ma'lumotlaringiz to‘g‘rimi?")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Tasdiqlayman", callback_data='confirm'),
               InlineKeyboardButton("✏️ O‘zgartirish", callback_data='edit'))

    send_callback_message(call, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'edit')
def restart_registration(call):
    chat_id = call.message.chat.id
    user_data.pop(chat_id, None)
    start(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'confirm')
def send_to_channel(call):
    chat_id = call.message.chat.id

    text = ("🆕 Yangi mijoz:\n\n"
            f"👤 Ism: {user_data[chat_id]['name']}\n"
            f"📞 Telefon: {user_data[chat_id]['phone']}\n"
            f"📍 Yo‘nalish: {user_data[chat_id]['route']}\n"
            f"🧑‍🤝‍🧑 Yo‘lovchilar: {user_data[chat_id]['passengers']} ta\n\n"
            "📢 @SwiftCabuz")

    bot.send_message("@SwiftCabuz", text)
    send_callback_message(call, "✅ Ma'lumotlaringiz qabul qilindi! 5 daqiqa ichida haydovchilar siz bilan bog'lanadi. Safaringiz behatar bo‘lsin! 🚖")

def run_bot():
    while True:
        try:
            logging.info("Bot ishga tushdi!")
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
