import logging

from aiogram_dialog import setup_dialogs
from aiogram import Bot, Dispatcher

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from config import Config
from aiogram.client.bot import DefaultBotProperties
from handlers.start_handler import test_dialog, test_router
from services.db import Database

storage = MemoryStorage()

bot = Bot(token=Config.TELEGRAM_API_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)

# logger

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_routers():
    
    dp.include_router(test_router)
    dp.include_router(test_dialog)


async def on_start():
    load_routers()
    logger.info("Routers loaded.")
    db = Database()
    await db.create_table()
    logger.info("Database connected.")
    setup_dialogs(dp)
    logger.info("Bot is up and running.")
