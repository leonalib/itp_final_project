from telebot import types
from database import save_order

def register_handlers(bot, user_data):

    def ask_size(chat_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🟢 Small (15 cm / 2–4)', callback_data='size_small'))
        markup.add(types.InlineKeyboardButton('🟡 Medium (20 cm / 6–8)', callback_data='size_medium'))
        markup.add(types.InlineKeyboardButton('🔴 Large (25 cm / 10–15)', callback_data='size_large'))
        markup.add(types.InlineKeyboardButton('📏 Custom size', callback_data='size_custom'))
        bot.send_message(chat_id, "Now choose the size:", reply_markup=markup)

    def show_order_summary(chat_id):
        data = user_data.get(chat_id, {})
        summary = (
            f"📋 *Order Summary:*\n\n"
            f"🍰 Flavor: {data.get('flavor', '—')}\n"
            f"📏 Size: {data.get('size', '—')}\n"
            f"✏️ Extras: {data.get('extras', '—')}\n\n"
            f"Confirm your order?"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('✅ Confirm', callback_data='confirm_order'),
            types.InlineKeyboardButton('❌ Cancel', callback_data='cancel_order')
        )
        bot.send_message(chat_id, summary, parse_mode='Markdown', reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        chat_id = call.message.chat.id
        if chat_id not in user_data:
            user_data[chat_id] = {}

        if call.data == 'Cake_flavor':
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton('🍫 Chocolate', callback_data='flavor_choco'),
                types.InlineKeyboardButton('🍦 Vanilla', callback_data='flavor_vanilla')
            )
            markup.add(
                types.InlineKeyboardButton('❤️ Red Velvet', callback_data='flavor_red_velvet'),
                types.InlineKeyboardButton('🍯 Honey', callback_data='flavor_honey')
            )
            markup.add(
                types.InlineKeyboardButton('🫐 Berry', callback_data='flavor_berry'),
                types.InlineKeyboardButton('✏️ Custom flavor', callback_data='flavor_custom')
            )
            bot.send_message(chat_id, "Choose your cake flavor:", reply_markup=markup)

        elif call.data.startswith("flavor_") and call.data != "flavor_custom":
            flavor_map = {
                "flavor_choco": "Chocolate",
                "flavor_vanilla": "Vanilla",
                "flavor_red_velvet": "Red Velvet",
                "flavor_honey": "Honey",
                "flavor_berry": "Berry"
            }
            user_data[chat_id]['flavor'] = flavor_map.get(call.data, call.data)
            ask_size(chat_id)

        elif call.data == "flavor_custom":
            user_data[chat_id]['waiting_for'] = 'flavor'
            bot.send_message(chat_id, "✏️ Enter your flavor:")

        elif call.data.startswith("size_") and call.data != "size_custom":
            size_map = {
                "size_small": "Small (15 cm / 2–4 servings)",
                "size_medium": "Medium (20 cm / 6–8 servings)",
                "size_large": "Large (25 cm / 10–15 servings)"
            }
            user_data[chat_id]['size'] = size_map.get(call.data)
            user_data[chat_id]['waiting_for'] = 'photo'
            bot.send_message(chat_id, "✅ Size saved! Now send a photo of your cake design 📸")

        elif call.data == "size_custom":
            user_data[chat_id]['waiting_for'] = 'size'
            bot.send_message(chat_id, "📏 Enter your custom size (e.g. 18 cm):")

        elif call.data == "confirm_order":
            data = user_data.get(chat_id, {})
            success = save_order(
                chat_id,
                call.message.chat.username or "unknown",
                data.get('flavor'),
                data.get('size'),
                data.get('photo'),
                data.get('extras')
            )
            if success:
                bot.send_message(chat_id, "🎉 Your order has been placed! We'll contact you soon.")
                user_data[chat_id] = {}
            else:
                bot.send_message(chat_id, "⚠️ Something went wrong. Please try again.")

        elif call.data == "cancel_order":
            user_data[chat_id] = {}
            bot.send_message(chat_id, "❌ Order cancelled. Send /start to begin again.")

    @bot.message_handler(content_types=['text'])
    def handle_text(message):
        chat_id = message.chat.id
        waiting = user_data.get(chat_id, {}).get('waiting_for')

        if waiting == 'flavor':
            user_data[chat_id]['flavor'] = message.text
            user_data[chat_id]['waiting_for'] = None
            bot.send_message(chat_id, f"✅ Flavor '{message.text}' saved!")
            ask_size(chat_id)
        elif waiting == 'size':
            user_data[chat_id]['size'] = message.text
            user_data[chat_id]['waiting_for'] = 'photo'
            bot.send_message(chat_id, "✅ Size saved! Now send a photo 📸")
        elif waiting == 'extras':
            user_data[chat_id]['extras'] = message.text
            user_data[chat_id]['waiting_for'] = None
            show_order_summary(chat_id)
        else:
            bot.send_message(chat_id, "Send /start to begin 🎂")

    @bot.message_handler(content_types=['photo'])
    def get_photo(message):
        chat_id = message.chat.id
        if user_data.get(chat_id, {}).get('waiting_for') == 'photo':
            user_data[chat_id]['photo'] = message.photo[-1].file_id
            user_data[chat_id]['waiting_for'] = 'extras'
            bot.send_message(chat_id, "📸 Photo saved! Now write any extras\n(e.g. text on cake, allergies, wishes):")
        else:
            bot.send_message(chat_id, "Please follow the steps. Send /start to begin.")