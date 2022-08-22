import json
import logging
import time

import requests
import telegram
from telegram import ParseMode
from telegram.ext import Updater
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.update import Update

BASE_URL_MIXNODE = "https://validator.nymtech.net/api/v1/status/mixnode/"
BASE_URL_STAKE = "/stake-saturation"
BASE_URL_EXPLORER = "https://sandbox-explorer.nymtech.net"
NG_APY = "https://mixnet.api.explorers.guru/api/mixnodes"

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
            stake = 0.0
            try:
                req = requests.get(BASE_URL_MIXNODE + mixnode['idkey'] + BASE_URL_STAKE)
                if req.ok:
                    stake = req.json().get('saturation')
            except requests.exceptions.RequestException as e:
                print(e)

            apy = 0.0
            try:
                req = requests.get(NG_APY,timeout=20)
                if req.ok:
                    apy = list(filter(lambda x: x["identityKey"] == mixnode['idkey'], req.json()))[0]['apy']
            except requests.exceptions.RequestException as e:
                print(e)

            msg += f"\n{mixnode['name']}"
            msg += f"\nIdentity Key: `{mixnode['idkey']}`"

            if stake > 0.0:
                msg += f"\nStake saturation: {stake * 100:.2f}%"
                msg += f"\n**Delegations accepted: {STATE_INACTIVE if stake > 0.99 else STATE_ACTIVE}**"

            if apy > 0.0:
                msg += f"\nAPY: {apy * 100:.2f}%"

            msg += f"\n[Explorer](https://explorer.nymtech.net/network-components/mixnode/{mixnode['idkey']})\n"

        return msg

    def start(self, update: Update, context: CallbackContext):
        username = update.message.from_user.username
        update.message.reply_text(
            f"Hello!\n[No Trust Verify](https://nym.notrustverify.ch) mixnodes are\n\n{TelegramBot.formatMixnodes(self.mixnodes)}\nVisit [nym.notrustverify.ch](https://nym.notrustverify.ch) or join us on [Telegram](https://t.me/notrustverify)",
            parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    def help(self, update: Update, context: CallbackContext):
        update.message.reply_text("Available Commands :"
                                  "\n\t/mixnodes - Retrieve No Trust Verify mixnodes")

    def getMixnodes(self, update: Update, context: CallbackContext):

        print(f"mixnode, Data {context.args}")
        msg = TelegramBot.formatMixnodes(self.mixnodes)
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    def unknown_text(self, update: Update, context: CallbackContext):
        print(f"unknown_text: {update.message.text}")
        update.message.reply_text(
            "Sorry I can't recognize you , you said '%s'" % update.message.text)

    def unknown(self, update: Update, context: CallbackContext):
        print(f"unknown: {update.message.text}")
        update.message.reply_text(
            "Sorry '%s' is not a valid command" % update.message.text)
