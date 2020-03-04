#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import schedule

from telegram.ext import Updater, CommandHandler


if not os.path.isfile('chats.txt'):
    f = open('chats.txt', 'w')
    f.close()


def start(update, context):
    try:
        chat_id = str(update.message.chat.id)
        with open('chats.txt', 'r+') as f:
            old = f.read()  # Also seeks to end
            if chat_id not in old:
                f.write(chat_id + '\n')
            else:
                return update.message.reply_text('Chat already subscribed!')
        update.message.reply_text(
            'This chat is now subscribed to daily AllToVibe reminders!'
        )
    except Exception as e:
        print('Error at /start:', e)
   

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def post_reminder(updater):
    print('Posting remainders...')
    with open('chats.txt', 'r') as f:
        chat_ids = [i.replace('\n', '') for i in f.readlines()]

    try:
        for chat_id in chat_ids:
            try:
                updater.bot.send_message(
                    chat_id,
                    'Hey! Remember to submit your daily AllToVibe!\n' +
                    'https://alltox.ayy.fi/'
                )
            except Exception as e:
                continue
            time.sleep(0.5)
    except Exception as e:
        print('Error at reminder :', e)


def main():
    """Start the bot."""
    TOKEN = os.environ['ALLTOVIBE_TOKEN']
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))

    # log all errors
    # dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # schedule.every().day.at("10:00").do(post_reminder, updater)
    schedule.every(5).seconds.do(post_reminder, updater)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    # updater.idle()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
