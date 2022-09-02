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
from utils import Utils

BASE_URL_MIXNODE = "https://validator.nymtech.net/api/v1/status/mixnode/"
BASE_URL_EXPLORER = "https://explorer.nymtech.net/api/v1/mix-node/"
BASE_URL_STAKE = "/stake-saturation"
NG_APY = "https://mixnet.api.explorers.guru/api/mixnodes"

STATE_INACTIVE = "🟥"
STATE_STANDBY = "🟦"
STATE_ACTIVE = "🟩"
STATE_ERROR = "🟨"

TIME_FORMAT = "%d.%m.%y %H:%M:%S"
UNYM = 10 ** 6


class TelegramBot:

    def __init__(self, telegramToken, filePath, queryApi):

        with open(filePath, "r") as fp:
            self.mixnodes = json.load(fp)

        self.token = telegramToken
        self.queryApi = queryApi

        self.updater = Updater(self.token, use_context=True)
        self.updater.dispatcher.add_handler(CommandHandler('start', self.start))
        self.updater.dispatcher.add_handler(CommandHandler('help', self.help))
        self.updater.dispatcher.add_handler(CommandHandler('mixnodes', self.getMixnodes))
        self.updater.dispatcher.add_handler(CommandHandler('m', self.getMixnodes))
        # self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.unknown))
        # self.updater.dispatcher.add_handler(MessageHandler(Filters.command, self.unknown))

        # Filters out unknown messages.
        # self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.unknown_text))

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
    def getData(url, session):

        try:
            req = session.get(url)
            if req.ok:
                return req
        except requests.exceptions.RequestException as e:
            print(e)
            return 0.0

    @staticmethod
    def formatMixnodes(mixnodes, queryApi):
        msg = ""

        s = requests.session()

        for mixnode in mixnodes['mixnodes']:
            amountStake = 0.0
            stake = 0.0
            apy = 0.0

            if queryApi:
                try:
                    amountStake = float(
                        TelegramBot.getData(BASE_URL_EXPLORER + mixnode['idkey'], s).json()['total_delegation'][
                            'amount'])
                except KeyError as e:
                    print(e)

                try:
                    amountStake /= UNYM
                except ZeroDivisionError as e:
                    print(e)

                try:
                    stake = TelegramBot.getData(BASE_URL_MIXNODE + mixnode['idkey'] + BASE_URL_STAKE, s).json()[
                        'saturation']
                except KeyError as e:
                    print(e)

                try:
                    apy = \
                        list(filter(lambda x: x["identityKey"] == mixnode['idkey'],
                                    TelegramBot.getData(NG_APY, s).json()))[0][
                            'apy']
                except KeyError as e:
                    print(e)

            try:
                msg += "\n"
                for user in mixnode.get('user'):
                    msg += f"[{user}](https://t.me/{user}) - "
            except TypeError as e:
                print(e)

            msg += f"{mixnode['name']}"
            msg += f"\nIdentity Key: `{mixnode['idkey']}`"

            if stake > 0.0:
                msg += f"\nStake saturation: {stake * 100:.2f}% ({Utils.humanFormat(amountStake, 2)} NYM)"
                msg += f"\n**Delegations accepted: {STATE_INACTIVE if stake > 0.99 else STATE_ACTIVE}**"

            if apy > 0.0:
                msg += f"\nAPY: {apy * 100:.2f}%"

            msg += f"\n[Explorer](https://explorer.nymtech.net/network-components/mixnode/{mixnode['idkey']})\n"

        return msg

    @staticmethod
    def formatLinks(links):
        msg = ""
        for link in links['links']:
            msg += f"\n🔗 [{link['description']}]({link['link']})\n"

        return msg

    def start(self, update: Update, context: CallbackContext):
        username = update.message.from_user.username
        update.message.reply_text(
            f"Hello!\nLes mixnodes de la [communauté francophone](https://t.me/nymfrench) sont \n\n{TelegramBot.formatMixnodes(self.mixnodes, self.queryApi)}\nRejoignez-nous sur [Telegram](https://t.me/nymfrench)",
            parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    def help(self, update: Update, context: CallbackContext):
        update.message.reply_text("Available Commands :"
                                  "\n\t/mixnodes - Retrieve mixnodes")

    def getMixnodes(self, update: Update, context: CallbackContext):

        print(f"mixnode, Data {context.args}")
        msg = TelegramBot.formatMixnodes(self.mixnodes, self.queryApi)

        if self.mixnodes.get('links') is not None:
            msg += TelegramBot.formatLinks(self.mixnodes)

        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    def unknown_text(self, update: Update, context: CallbackContext):
        print(f"unknown_text: {update.message.text}")
        update.message.reply_text(
            "Sorry I can't recognize you , you said '%s'" % update.message.text)

    def unknown(self, update: Update, context: CallbackContext):
        print(f"unknown: {update.message.text}")
        update.message.reply_text(
            "Sorry '%s' is not a valid command" % update.message.text)
