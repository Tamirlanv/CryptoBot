import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from handlers import router
from database import init_db
from alerts import alerts_worker


load_dotenv()

bot = Bot(os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher()
dp.include_router(router)

logging.basicConfig(
    level=logging.DEBUG,   
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logging.getLogger("aiogram").setLevel(logging.INFO)
logging.getLogger("aiohttp").setLevel(logging.INFO)


async def main():
    init_db()
    asyncio.create_task(alerts_worker(bot))
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("exist")
    