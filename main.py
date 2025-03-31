import asyncio
import json
import dotenv
import bot
import utils


async def run_pinger_loop():
    print("Ping loop started!")
    env = dotenv.dotenv_values(".env")
    while True:
        with open("config.json", "r", encoding="utf-8") as f:
            projects_to_ping = json.load(f)["projects_to_ping"]
        projects_to_ping = filter(lambda x: not x["ignore_ping_loop"], projects_to_ping)
        for project in projects_to_ping:
            res = await utils.ping_url(project["ping_url"])
            if not res[0]:
                markup = bot.TeleTypes.InlineKeyboardMarkup()
                markup.add(bot.TeleTypes.InlineKeyboardButton(
                    text='Проверить',
                    callback_data=f"ping_project/{project["id"]}"
                ))
                await bot.bot.send_message(
                    chat_id=env["ADMIN_CHAT_ID"],
                    text=f"Проект *{project["title"]}* ответил на пинг с ошибкой!",
                    reply_markup=markup
                )
        await asyncio.sleep(60*5)


async def main():
    task1 = asyncio.create_task(bot.run())
    task2 = asyncio.create_task(run_pinger_loop())
    await task1
    await task2

asyncio.run(main())
