import logging

from dotenv import load_dotenv
import os
from bot import TelegramBot

MIXNODES_FILE = "data/nodes.json"


def main(telegramToken):
    bot = TelegramBot(telegramToken, filePath=MIXNODES_FILE)

    bot.startBot()


if __name__ == '__main__':
    load_dotenv()

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    main(TELEGRAM_TOKEN)
