import threading
import time
from telebot import telebot, types
import dtb_module
import links_module
import os

TG_TOKEN = os.environ.get('TG_TOKEN')

WELCOME_MESSAGE = """
Hey there!
I can shorten links and do other things🧙🔮:

🔗 Send long URL and receive short URL
🔗 Send short URL and receive links count
🔗 Also receive top links by count

If any problems contact 👨🏻‍💻[admin](tg://user?id=360841329)
"""

bot = telebot.TeleBot(TG_TOKEN)
ABOUT = "About me"
TOP_LINKS = "See top links"
SHORTEN_URL = "Shorten URL"
COUNT_CLICKS = "Check clicks"
TOP_24 = 'Top links in 24 hours'
TOP_ALL = 'Top links all time'


def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.InlineKeyboardButton(text=ABOUT))
    markup.add(types.InlineKeyboardButton(text=TOP_LINKS))
    markup.add(types.InlineKeyboardButton(text=SHORTEN_URL))
    markup.add(types.InlineKeyboardButton(text=COUNT_CLICKS))
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    keyboard = get_main_keyboard()
    bot.send_message(message.chat.id,
                     text=WELCOME_MESSAGE,
                     reply_markup=keyboard,
                     disable_web_page_preview=True,
                     parse_mode="markdown")


@bot.message_handler(regexp=f'^{ABOUT}$')
def send_about(message):
    keyboard = get_main_keyboard()
    bot.reply_to(message,
                 text=WELCOME_MESSAGE,
                 reply_markup=keyboard,
                 disable_web_page_preview=True,
                 parse_mode="markdown")


@bot.message_handler(regexp=f'^{SHORTEN_URL}$')
def send_shorten_url(message):
    keyboard = get_main_keyboard()
    bot.reply_to(message,
                 text="Please type long URL here to receive short one:",
                 reply_markup=keyboard,
                 disable_web_page_preview=True,
                 parse_mode="markdown")


@bot.message_handler(regexp=f'^{COUNT_CLICKS}$')
def send_clicks_count(message):
    keyboard = get_main_keyboard()
    bot.reply_to(message,
                 text="Please type short URL here to receive clicks count per month:",
                 reply_markup=keyboard,
                 disable_web_page_preview=True,
                 parse_mode="markdown")


def get_top_links_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.InlineKeyboardButton(text=TOP_24, callback_data=TOP_24))
    markup.add(types.InlineKeyboardButton(text=TOP_ALL, callback_data=TOP_ALL))
    markup.add(types.InlineKeyboardButton(text=ABOUT))
    return markup


@bot.message_handler(regexp=f'^{TOP_LINKS}$')
def send_top_links(message):
    keyboard = get_top_links_keyboard()
    bot.send_message(message.chat.id, text='Choose period', reply_markup=keyboard)


@bot.message_handler(regexp=f'^{TOP_24}$')
def top_24_handler(call):
    keyboard = get_top_links_keyboard()
    created_after = int(time.time() - 86400)
    stats = dtb_module.get_top_links(user_id=call.from_user.id, created_after=created_after)
    response = ''
    for link, clicks in stats:
        response += f'Links clicks count for {link} last 24 hours = {clicks}\n'
    try:
        bot.send_message(call.from_user.id, text=response, disable_web_page_preview=True, reply_markup=keyboard)
    except:
        bot.send_message(call.from_user.id, text="No links found, try something else.", disable_web_page_preview=True, reply_markup=keyboard)


@bot.message_handler(regexp=f'^{TOP_ALL}$')
def top_all(call):
    keyboard = get_top_links_keyboard()
    stats = dtb_module.get_top_links(user_id=call.from_user.id)
    response = ''
    for link, clicks in stats:
        response += f'Links clicks count for {link} at all times = {clicks}\n'
    try:
        bot.send_message(call.from_user.id, text=response, disable_web_page_preview=True, reply_markup=keyboard)
    except:
        bot.send_message(call.from_user.id, text="No links found, try something else.", disable_web_page_preview=True, reply_markup=keyboard)


@bot.message_handler()
def message_processor(message):
    keyboard = get_main_keyboard()
    if message.text.startswith('https://bitly.is') \
            or message.text.startswith('bitly.is')\
            or message.text.startswith('https://bit.ly')\
            or message.text.startswith('bit.ly'):
        clicks = links_module.get_clicks_count(message.text)
        if isinstance(clicks, int):
            bot.reply_to(message, text=f'Your short link had {clicks} clicks this month.', reply_markup=keyboard)
        else:
            bot.reply_to(message, text='Bad URL, please retry!', reply_markup=keyboard)
        dtb_module.update_link_clicks(short_link=message.text, clicks=clicks)
    else:
        short_link = links_module.shorten_url(link=message.text)
        if isinstance(short_link, int):
            bot.reply_to(message, text='Bad URL, please retry!', reply_markup=keyboard)
        else:
            bot.reply_to(message, text=f'Your short link for this URL: {short_link}', reply_markup=keyboard)
        dtb_module.create_link_record(user_id=message.from_user.id,
                                      long_link=message.text,
                                      short_link=short_link,
                                      created_at=int(time.time()))


def click_updater():
    while True:
        print("Update clicks start...\n")
        offset = 0
        while True:
            rows = dtb_module.get_clicks(limit=10, offset=offset)
            # print(rows)
            if not rows:
                break
            for old_clicks, link in rows:
                print(f'Current clicks count for {link} is {old_clicks}')
                clicks_count = links_module.get_clicks_count(link=link)
                if isinstance(clicks_count, int) and clicks_count != old_clicks:
                    dtb_module.update_link_clicks(short_link=link, clicks=clicks_count)
                    print(f'Clicks count for {link} updated from {old_clicks} to {clicks_count}\n')
                else:
                    print(f'Clicks count for {link} no update from {clicks_count}\n')
            offset += 10
        print("...clicks update complete.")
        break


threading.Thread(target=click_updater()).start()

bot.polling()

