import logging

from dotenv import load_dotenv
import os
from bot import TelegramBot

BASE_URL_MIXNODE = "https://sandbox-validator.nymtech.net/api/v1/status/mixnode"
BASE_URL_GW = "https://sandbox-validator.nymtech.net/api/v1/status/gateway"
BASE_URL_EXPLORER = "https://sandbox-explorer.nymtech.net"
MIXNODES_FILE = "data/mixnodes.json"


def main(telegramToken):
    bot = TelegramBot(telegramToken, filePath=MIXNODES_FILE)

    bot.startBot()


if __name__ == '__main__':
    load_dotenv()

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    main(TELEGRAM_TOKEN)
