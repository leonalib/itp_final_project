import telebot
from config import TOKEN
from database import create_table
from handlers import register_handlers
from admin import register_admin_handlers  

bot = telebot.TeleBot('7995858623:AAEN41vp-1wedmDzRBK5OfN8HA6-EhZUycU')
user_data = {}

create_table()

register_admin_handlers(bot) 

@bot.message_handler(commands=['start', 'hello'])
def additional_btns(message):
    from telebot import types
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🎂 Cake flavor', callback_data='Cake_flavor')
    markup.row(btn1)
    bot.send_message(
        message.chat.id,
        f"Hi {message.from_user.first_name or ''}! 🎂\n"
        f"I'm your cake assistant. Let's build the perfect cake!\n"
        f"Start by choosing a flavor 👇",
        reply_markup=markup
    )


register_handlers(bot, user_data)

bot.polling(non_stop=True)