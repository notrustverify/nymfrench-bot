import logging

from dotenv import load_dotenv
import os
from bot import TelegramBot

MIXNODES_FILE = "data/nodes.json"


def main(telegramToken,queryApi):
    bot = TelegramBot(telegramToken, MIXNODES_FILE,queryApi)

    bot.startBot()


if __name__ == '__main__':
    load_dotenv()

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    QUERY_API = os.getenv("QUERY_API","False").lower() in ('true', '1', 't')
    
    main(TELEGRAM_TOKEN,QUERY_API)
