#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import os
from random import random
import logging
import requests
from io import BytesIO
from PIL import Image

from telegram.ext import Updater, CommandHandler

kehys = Image.open('./kehys.png', 'r')
kehys_bw = Image.open('./kehys_bw.png', 'r')
kehys_inv = Image.open('./kehys_inv.png', 'r')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def taulu(update, context):
    """Send a message when the command /taulu is issued."""
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    query = context.bot.get_user_profile_photos(user_id, limit=1)
    photo = query.photos[0][-1].get_file()
    url = photo.file_path

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    dice = random()
    _kehys = kehys
    if dice >= 0.99:
        _kehys = kehys_bw
    if dice >= 0.999:
        _kehys = kehys_inv

    _kehys = _kehys.resize(img.size)
    img.paste(_kehys, (0, 0), _kehys)
    filename = 'images/img_{}.png'.format(user_id)
    img.save(filename, format='PNG')

    f = open(filename, 'rb')
    context.bot.send_photo(chat_id, f)
    os.remove(filename)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN = os.environ['fspx_taulubot_token']
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("taulu", taulu))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
