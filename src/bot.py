from loader import on_start, dp, bot
from asyncio import run


async def main():
    await on_start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    run(main())  
