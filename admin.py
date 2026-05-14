from datetime import datetime
from telebot import types
from config import ADMIN_IDS
from database import (
    get_orders, get_order_by_id,
    update_order_status, get_stats
)


STATUS_LABELS = {
    'new':         '🆕 New',
    'in_progress': '🔧 In Progress',
    'ready':       '✅ Ready',
    'delivered':   '🚚 Delivered',
    'cancelled':   '❌ Cancelled',
}

STATUS_NEXT = {
    'new':         'in_progress',
    'in_progress': 'ready',
    'ready':       'delivered',
}


CUSTOMER_MESSAGES = {
    'in_progress': "🔧 Your order *#{id}* is now *in progress*! We've started making your cake. 🎂",
    'ready':       "✅ Great news! Your order *#{id}* is *ready*! We'll arrange delivery soon. 🎉",
    'delivered':   "🚚 Your order *#{id}* has been *delivered*! Enjoy your cake! 🎂❤️",
    'cancelled':   "❌ Your order *#{id}* has been *cancelled*. Please contact us for details.",
}




def is_admin(chat_id):
    return chat_id in ADMIN_IDS


def notify_admins(bot, text, photo_id=None, markup=None):
    """Push a message to every admin ID."""
    for admin_id in ADMIN_IDS:
        try:
            if photo_id:
                bot.send_photo(admin_id, photo_id,
                               caption=text, parse_mode='Markdown',
                               reply_markup=markup)
            else:
                bot.send_message(admin_id, text,
                                 parse_mode='Markdown',
                                 reply_markup=markup)
        except Exception as e:
            print(f"Could not notify admin {admin_id}: {e}")


def notify_new_order(bot, order_id, chat_id, username, data):
    """Called from handlers.py right after a customer confirms an order."""
    username_display = f"@{username}" if username != "unknown" else f"ID: {chat_id}"
    text = (
        f"🆕 *New Order #{order_id}!*\n\n"
        f"👤 Customer: {username_display}\n"
        f"🍰 Flavor: {data.get('flavor', '-')}\n"
        f"📏 Size: {data.get('size', '-')}\n"
        f"✏️ Extras: {data.get('extras', '-')}\n"
        f"🕐 {datetime.now().strftime('%d %b %Y, %H:%M')}"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('🔧 Accept & Start',
                                   callback_data=f'adm_status_{order_id}_in_progress'),
        types.InlineKeyboardButton('❌ Decline',
                                   callback_data=f'adm_status_{order_id}_cancelled'),
    )
    markup.add(
        types.InlineKeyboardButton('📋 Open Order',
                                   callback_data=f'adm_detail_{order_id}'),
    )
    notify_admins(bot, text, photo_id=data.get('photo'), markup=markup)




def send_admin_menu(bot, chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('🆕 New',         callback_data='adm_list_new'),
        types.InlineKeyboardButton('🔧 In Progress', callback_data='adm_list_in_progress'),
    )
    markup.add(
        types.InlineKeyboardButton('✅ Ready',        callback_data='adm_list_ready'),
        types.InlineKeyboardButton('📦 All Orders',   callback_data='adm_list_all'),
    )
    markup.add(
        types.InlineKeyboardButton('📊 Statistics',   callback_data='adm_stats'),
    )
    bot.send_message(
        chat_id,
        "👑 *Admin Panel — Cake Orders*\n\nChoose a view:",
        parse_mode='Markdown',
        reply_markup=markup,
    )


def show_orders_list(bot, chat_id, status_filter=None):
    rows = get_orders(status_filter=status_filter if status_filter != 'all' else None)

    if not rows:
        label = STATUS_LABELS.get(status_filter, 'all') if status_filter else 'all'
        bot.send_message(chat_id, f"📭 No orders — status: {label}")
        return

    label = (
        STATUS_LABELS.get(status_filter, '📦 All')
        if status_filter and status_filter != 'all'
        else '📦 All'
    )
    header = f"*{label} Orders (last {len(rows)}):*\n\n"
    lines = []
    markup = types.InlineKeyboardMarkup()

    for row in rows:
        oid, cid, username, flavor, size, photo_id, extras, status, created_at = row
        icon = STATUS_LABELS.get(status, status)
        date = created_at.strftime('%d %b, %H:%M') if created_at else '-'
        lines.append(f"#{oid} | {icon} | @{username or '-'} | {flavor} | {date}")
        markup.add(
            types.InlineKeyboardButton(
                f"#{oid}  {flavor}  —  {icon}",
                callback_data=f'adm_detail_{oid}',
            )
        )

    markup.add(types.InlineKeyboardButton('🔙 Menu', callback_data='adm_menu'))
    bot.send_message(
        chat_id,
        header + "\n".join(lines),
        parse_mode='Markdown',
        reply_markup=markup,
    )


def show_order_detail(bot, chat_id, order_id):
    row = get_order_by_id(order_id)
    if not row:
        bot.send_message(chat_id, f"❌ Order #{order_id} not found.")
        return

    oid, cid, username, flavor, size, photo_id, extras, status, created_at = row
    date = created_at.strftime('%d %b %Y, %H:%M') if created_at else '-'
    status_label = STATUS_LABELS.get(status, status)

    text = (
        f"📋 *Order #{oid}*\n\n"
        f"👤 Customer: @{username or '-'}  (`{cid}`)\n"
        f"🍰 Flavor: {flavor or '-'}\n"
        f"📏 Size: {size or '-'}\n"
        f"✏️ Extras: {extras or '-'}\n"
        f"📌 Status: {status_label}\n"
        f"🕐 Created: {date}"
    )

    markup = types.InlineKeyboardMarkup()

    # Advance to next status
    if status in STATUS_NEXT:
        nxt = STATUS_NEXT[status]
        markup.add(
            types.InlineKeyboardButton(
                f"➡️ Mark as {STATUS_LABELS[nxt]}",
                callback_data=f'adm_status_{oid}_{nxt}',
            )
        )

    
    if status not in ('delivered', 'cancelled'):
        markup.add(
            types.InlineKeyboardButton(
                '❌ Cancel Order',
                callback_data=f'adm_status_{oid}_cancelled',
            )
        )

    markup.add(
        types.InlineKeyboardButton('💬 Message Customer', url=f'tg://user?id={cid}')
    )
    markup.add(
        types.InlineKeyboardButton('🔙 Back to List', callback_data='adm_list_all')
    )

    if photo_id:
        bot.send_photo(chat_id, photo_id,
                       caption=text, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)


def do_update_status(bot, chat_id, order_id, new_status):
    result = update_order_status(order_id, new_status)
    if not result:
        bot.send_message(chat_id, f"❌ Order #{order_id} not found.")
        return

    client_chat_id, flavor = result
    status_label = STATUS_LABELS.get(new_status, new_status)
    bot.send_message(chat_id, f"✅ Order #{order_id} → {status_label}")

    
    template = CUSTOMER_MESSAGES.get(new_status)
    if template:
        try:
            bot.send_message(
                client_chat_id,
                template.format(id=order_id),
                parse_mode='Markdown',
            )
        except Exception as e:
            print(f"Could not notify customer {client_chat_id}: {e}")


def show_stats(bot, chat_id):
    counts, periods = get_stats()
    new_c, in_prog_c, ready_c, delivered_c, cancelled_c, total = counts
    week_c, month_c = periods

    text = (
        f"📊 *Order Statistics*\n\n"
        f"🆕 New:          {new_c}\n"
        f"🔧 In Progress:  {in_prog_c}\n"
        f"✅ Ready:        {ready_c}\n"
        f"🚚 Delivered:    {delivered_c}\n"
        f"❌ Cancelled:    {cancelled_c}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📦 Total:        {total}\n\n"
        f"📅 Last 7 days:  {week_c}\n"
        f"📅 Last 30 days: {month_c}"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🔙 Menu', callback_data='adm_menu'))
    bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)




def register_admin_handlers(bot):
    """Register all admin callbacks and commands. Call once from main.py."""

    # ── Inline button callbacks (all prefixed "adm_") ──
    @bot.callback_query_handler(func=lambda call: call.data.startswith('adm_'))
    def admin_callback(call):
        chat_id = call.message.chat.id

        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "Access denied.")
            return

        data = call.data

        if data == 'adm_menu':
            send_admin_menu(bot, chat_id)

        elif data == 'adm_stats':
            show_stats(bot, chat_id)

        elif data.startswith('adm_list_'):
            status = data.replace('adm_list_', '')
            show_orders_list(bot, chat_id,
                             status_filter=None if status == 'all' else status)

        elif data.startswith('adm_detail_'):
            try:
                order_id = int(data.replace('adm_detail_', ''))
                show_order_detail(bot, chat_id, order_id)
            except ValueError:
                pass

        elif data.startswith('adm_status_'):
            # format: adm_status_{order_id}_{new_status}
            parts = data.replace('adm_status_', '').split('_', 1)
            try:
                order_id  = int(parts[0])
                new_status = parts[1]
                do_update_status(bot, chat_id, order_id, new_status)
                show_order_detail(bot, chat_id, order_id)
            except (ValueError, IndexError):
                pass

        bot.answer_callback_query(call.id)

    
    @bot.message_handler(
        func=lambda m: is_admin(m.chat.id) and m.text and m.text.startswith('/')
    )
    def admin_commands(message):
        chat_id = message.chat.id
        cmd = message.text.strip()

        if cmd in ('/start', '/menu'):
            send_admin_menu(bot, chat_id)
        elif cmd == '/orders':
            show_orders_list(bot, chat_id, status_filter='new')
        elif cmd == '/allorders':
            show_orders_list(bot, chat_id, status_filter=None)
        elif cmd == '/stats':
            show_stats(bot, chat_id)
        elif cmd.startswith('/order '):
            try:
                order_id = int(cmd.split()[1])
                show_order_detail(bot, chat_id, order_id)
            except (IndexError, ValueError):
                bot.send_message(chat_id, "Usage: /order <id>")