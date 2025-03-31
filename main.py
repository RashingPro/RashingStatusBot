import asyncio
import bot


async def main():
    task1 = asyncio.create_task(bot.run())
    await task1

asyncio.run(main())
