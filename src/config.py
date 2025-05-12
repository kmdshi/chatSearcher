import os
import sys
from dotenv import load_dotenv

env = "prod"
if len(sys.argv) > 1 and sys.argv[1] == "dev":
    env = "dev"

env_file = "src/.env.dev" if env == "dev" else "src/.env"
load_dotenv(dotenv_path=env_file)


class Config:
    TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
    ADMIN_IDS = os.getenv("ADMIN_IDS")
    DB_PATH = os.getenv("DB_PATH")
