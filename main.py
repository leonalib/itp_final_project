import telebot
import webbrowser
from telebot import types
import psycopg2

conn = psycopg2.connect(
    dbname="Cake_Helper",
    user="postgres",
    password="1234",
    host="localhost"
)
cur = conn.cursor()

bot = telebot.TeleBot('7995858623:AAHM9KuUyIKuF8mgE5H0Gxg4JTC9sHQyHTM')

user_data = {}

@bot.message_handler(commands=['start', 'hello', 'привет'])
def additional_btns(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Cake flavor', callback_data='Cake_flavor')

    markup.row(btn1)

    bot.send_message(
        message.chat.id, 
        f'Hi! {message.from_user.first_name or ''} {message.from_user.last_name or ''}🎂! I’m your cake assistant. I’ll help you assemble the perfect cake for any occasion: birthday, celebration, or just a sweet mood😊.    Lets start with flavor!', 
        reply_markup=markup)
    
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    # создаём словарь если нет
    if chat_id not in user_data:
        user_data[chat_id] = {}

    # 👉 если нажали "Cake flavor"
    if call.data == 'Cake_flavor':
        markup = types.InlineKeyboardMarkup()

        btn1 = types.InlineKeyboardButton('Chocolate', callback_data='flavor_choco')
        btn2 = types.InlineKeyboardButton('Vanilla', callback_data='flavor_vanilla')
        btn3 = types.InlineKeyboardButton('Red Velvet', callback_data='flavor_red_velvet')
        btn4 = types.InlineKeyboardButton('Honey', callback_data='flavor_honey')
        btn5 = types.InlineKeyboardButton('Berry', callback_data='flavor_berry')
        btn6 = types.InlineKeyboardButton('Your own (enter)', callback_data='flavor_custom')

        markup.add(btn1, btn2)
        markup.add(btn3, btn4)
        markup.add(btn5, btn6)

        bot.send_message(chat_id, "Choose your cake flavor:", reply_markup=markup)

    # если выбрали готовый вкус
    elif call.data.startswith("flavor_") and call.data != "flavor_custom":
        flavor = call.data.split("_", 1)[1]
        user_data[chat_id]['flavor'] = flavor

        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('🟢 Small (15 cm / 2–4 servings)', callback_data='size_small')
        btn2 = types.InlineKeyboardButton('🟡 Medium (20 cm / 6–8 servings)', callback_data='size_medium')
        btn3 = types.InlineKeyboardButton('🔴 Large (25 cm / 10–15 servings)', callback_data='size_large')
        btn4 = types.InlineKeyboardButton('🎂 Custom size', callback_data='size_custom')


        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)
        markup.add(btn4)

        bot.send_message(chat_id, "Saved! Now choose a size:", reply_markup=markup)

    # если нажали "свой вкус"
    elif call.data == "flavor_custom":
        user_data[chat_id]['waiting_for_flavor'] = True
        bot.send_message(chat_id, "Enter your flavor:")

    elif call.data.startswith("size_") and call.data != "size_custom":
        size = call.data.split("_", 1)[1]

        if size == "small":
            user_data[chat_id]['size'] = "Small (15 cm)"
        elif size == "medium":
            user_data[chat_id]['size'] = "Medium (20 cm)"
        elif size == "large":
            user_data[chat_id]['size'] = "Large (25 cm)"

        # 👉 ждем фото
        user_data[chat_id]['waiting_for_photo'] = True

        bot.send_message(chat_id, "Size saved! Now send a photo of your cake design 📸")

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    chat_id = message.chat.id

    if user_data.get(chat_id, {}).get('waiting_for_photo'):
        file_id = message.photo[-1].file_id
        user_data[chat_id]['photo'] = file_id
        user_data[chat_id]['waiting_for_photo'] = False

        # теперь ждём extras
        user_data[chat_id]['waiting_for_extras'] = True

        bot.send_message(chat_id, "Photo saved! Now write any extras (text on cake, wishes, etc.) ✏️")
    


bot.polling(non_stop=True)