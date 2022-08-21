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

        with open(filePath,"r") as fp:
            self.mixnodes = json.load(fp)

        print(self.mixnodes)
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
        update.message.reply_text(f"Hello, {username}!\n"
                                  f"No Trust Verify mixnodes are\n{+TelegramBot.formatMixnodes(self.mixnodes)}")

    def help(self, update: Update, context: CallbackContext):
        update.message.reply_text("Available Commands :"
                                  "\n\t/mixnodes.json - Retrieve No Trust Verify mixnodes.json identity key")

    def getMixnodes(self, update: Update, context: CallbackContext):

        print(f"mixnode, Data {context.args}")
        msg = f"Availables mixnodes\n\n"+TelegramBot.formatMixnodes(self.mixnodes)
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    def remove(self, update: Update, context: CallbackContext):
        if update.edited_message:
            self.logHandler.error(f"remove() Edited message from {update.edited_message.from_user.id}")
            return

        if len(context.args) == 1:
            idKey = bleach.clean(context.args[0])
            status = self.nymRest.getStatus(idKey)

            if status == 'invalid':
                self.logHandler.error(f"mixnode, Data {context.args}")
                update.message.reply_text(f"Mixnode {idKey} not found")
            elif status is None:
                self.logHandler.error(f"mixnode, Data {context.args}")
                update.message.reply_text(f"Error with mixnode {idKey}")
            else:
                if self.delData(update.message.from_user.id, idKey, False):
                    update.message.reply_text(
                        f"mixnode {idKey} removed")
                else:
                    update.message.reply_text(
                        f"No mixnode with {idKey} for you")

        else:
            update.message.reply_text(
                f"Error: Usage /mixnode mixnode identity key")

    def unknown_text(self, update: Update, context: CallbackContext):
        print(f"unknown_text: {update.message.text}")
        update.message.reply_text(
            "Sorry I can't recognize you , you said '%s'" % update.message.text)

    def unknown(self, update: Update, context: CallbackContext):
        print(f"unknown: {update.message.text}")
        update.message.reply_text(
            "Sorry '%s' is not a valid command" % update.message.text)
