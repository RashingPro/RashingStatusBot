import asyncio
import json
import logging
import dotenv

from telebot import types as TeleTypes
from telebot.async_telebot import AsyncTeleBot

import utils

# init .env
env = dotenv.dotenv_values(".env")
TOKEN = env["TOKEN"]

# config logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# config bot
bot = AsyncTeleBot(TOKEN, parse_mode='Markdown', disable_web_page_preview=True, colorful_logs=True)


@bot.callback_query_handler(func=lambda call: call.data == "menu")
@bot.message_handler(commands=['start'])
async def cmd_start(call: TeleTypes.Message | TeleTypes.CallbackQuery):
    if isinstance(call, TeleTypes.Message):
        message = call
    else:
        message = call.message

    markup = TeleTypes.InlineKeyboardMarkup()
    with open("config.json", "r", encoding="utf-8") as f:
        projects_to_ping = json.load(f)["projects_to_ping"]
    full_row_len = 3
    full_row_count = len(projects_to_ping) // full_row_len
    reminder = len(projects_to_ping) % full_row_len
    for i in range(full_row_count):
        tba = []
        for j in range(i*full_row_len, (i+1)*full_row_len):
            tba.append(TeleTypes.InlineKeyboardButton(
                text=projects_to_ping[j]['title'],
                callback_data=f"ping_project/{projects_to_ping[j]['id']}"
            ))
        markup.add(*tba)
    tba = []
    for i in range(full_row_len*full_row_count, full_row_len*full_row_count + reminder):
        tba.append(TeleTypes.InlineKeyboardButton(
            text=projects_to_ping[i]['title'],
            callback_data=f"ping_project/{projects_to_ping[i]['id']}"
        ))
    markup.add(*tba)
    if isinstance(call, TeleTypes.Message):
        await bot.send_message(
            chat_id=message.chat.id,
            text='*Список проектов*',
            reply_markup=markup
        )
    else:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id,
            text='*Список проектов*',
            reply_markup=markup
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("ping_project/"))
async def ping_project(call: TeleTypes.CallbackQuery):
    id = int(call.data.split("/")[1])
    with open("config.json", "r", encoding="utf-8") as f:
        projects_to_ping: list = json.load(f)["projects_to_ping"]
    filter(lambda x: x["id"] == id, projects_to_ping)
    url = projects_to_ping[0]["url"]
    ping_url = projects_to_ping[0]["ping_url"]
    message_temp = await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text="Подождите, получаю статус проекта..."
    )
    res = await utils.ping_url(ping_url)
    text = f"*Проект {projects_to_ping[0]["title"]}*"
    text += f"\nURL: {url}"
    if res[0]:
        text += f"\nСтатус: 🟢В норме"
    else:
        text += f"\nСтатус: 🔴Ошибка"

    markup = TeleTypes.InlineKeyboardMarkup()
    markup.add(TeleTypes.InlineKeyboardButton(
        text='🔃 Обновить',
        callback_data=call.data
    ))
    markup.add(TeleTypes.InlineKeyboardButton(
        text='⬅ Назад',
        callback_data='menu'
    ))

    await bot.edit_message_text(
        chat_id=message_temp.chat.id,
        message_id=message_temp.id,
        text=text,
        reply_markup=markup
    )


async def run():
    print("Bot started!")
    await bot.infinity_polling(None, logger_level=logging.WARN)
