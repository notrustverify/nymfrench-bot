import json
import logging
import time

import telegram
from telegram import ParseMode
from telegram.ext import Updater
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.update import Update

BASE_URL_MIXNODE = "https://sandbox-validator.nymtech.net/api/v1/status/mixnode"
BASE_URL_EXPLORER = "https://sandbox-explorer.nymtech.net"

STATE_INACTIVE = "🟥"
STATE_STANDBY = "🟦"
STATE_ACTIVE = "🟩"
STATE_ERROR = "🟨"

TIME_FORMAT = "%d.%m.%y %H:%M:%S"


class TelegramBot:

    def __init__(self, telegramToken, filePath):

        with open(filePath, "r") as fp:
            self.mixnodes = json.load(fp)

        self.token = telegramToken

        self.updater = Updater(self.token, use_context=True)
        self.updater.dispatcher.add_handler(CommandHandler('start', self.start))
        self.updater.dispatcher.add_handler(CommandHandler('help', self.help))
        self.updater.dispatcher.add_handler(CommandHandler('mixnodes', self.getMixnodes))
        self.updater.dispatcher.add_handler(CommandHandler('m', self.getMixnodes))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.unknown))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.command, self.unknown))

        # Filters out unknown messages.
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.unknown_text))

        print(f"Start {__name__}")

    def startBot(self):
        try:
            self.updater.start_polling(bootstrap_retries=50, timeout=30)
        except Exception as e:
            print(e)

    def send(self, user, msg):
        for __ in range(10):
            try:
                bot = telegram.Bot(token=self.token)
                bot.sendMessage(int(user), text=msg, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            except telegram.error.RetryAfter as ra:
                print(e)

                if int(ra.retry_after) > 60:
                    print("Flood control exceeded. Retry in 60 seconds")
                    time.sleep(60)
                else:
                    time.sleep(int(ra.retry_after))
                continue
            except Exception as e:
                print(e)
            else:
                break

    @staticmethod
    def formatMixnodes(mixnodes):
        msg = ""
        for mixnode in mixnodes['mixnodes']:
            msg += f"{mixnode['name']}\n`{mixnode['idkey']}`\n\n"

        return msg

    def start(self, update: Update, context: CallbackContext):
        username = update.message.from_user.username
        update.message.reply_text(f"Hello!\n[No Trust Verify](https://nym.notrustverify.ch) mixnodes are\n\n{TelegramBot.formatMixnodes(self.mixnodes)}\nVisit [nym.notrustverify.ch](https://nym.notrustverify.ch) or join us on [Telegram](https://t.me/notrustverify)",
                                  parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    def help(self, update: Update, context: CallbackContext):
        update.message.reply_text("Available Commands :"
                                  "\n\t/mixnodes.json - Retrieve No Trust Verify mixnodes.json identity key")

    def getMixnodes(self, update: Update, context: CallbackContext):

        print(f"mixnode, Data {context.args}")
        msg = f"Available mixnodes\n\n" + TelegramBot.formatMixnodes(self.mixnodes)
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    def unknown_text(self, update: Update, context: CallbackContext):
        print(f"unknown_text: {update.message.text}")
        update.message.reply_text(
            "Sorry I can't recognize you , you said '%s'" % update.message.text)

    def unknown(self, update: Update, context: CallbackContext):
        print(f"unknown: {update.message.text}")
        update.message.reply_text(
            "Sorry '%s' is not a valid command" % update.message.text)
