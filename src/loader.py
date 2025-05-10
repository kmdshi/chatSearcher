import logging

from handlers import start_handler, chats_handler, additional_handler, adding_handler
from aiogram_dialog import setup_dialogs
from aiogram import Bot, Dispatcher

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from config import Config
from aiogram.client.bot import DefaultBotProperties
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
    dp.include_router(start_handler.start_router)
    dp.include_router(additional_handler.additional_router)
    dp.include_router(adding_handler.adding_router)
    dp.include_router(chats_handler.chats_dialog)
    dp.include_router(chats_handler.chats_router)


async def on_start():
    load_routers()
    logger.info("Routers loaded.")
    db = Database()
    await db.create_table()
    logger.info("Database connected.")
    setup_dialogs(dp)
    logger.info("Bot is up and running.")
