import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG") == "1"
AMQP_URI = os.getenv("AMQP_URI")
DATABASE_URI = os.getenv("DATABASE_URI")
CACHE_URI = os.getenv("CACHE_URI")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PROJECT_MAIL = os.getenv("PROJECT_MAIL")
MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")
