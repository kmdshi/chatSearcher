import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
