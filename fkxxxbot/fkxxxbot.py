import os

from telegram.ext import Updater, MessageHandler, Filters

TOKEN = os.environ['FKXXXBOT_TOKEN']

FKXXX_ID = -1001331753570


def forward_message(msg, chat_id, debug=False):
    if msg.text:
        updater.bot.send_message(chat_id, msg.text)
    elif msg.sticker:
        updater.bot.send_sticker(chat_id, msg.sticker.file_id)
    elif msg.photo:
        updater.bot.send_photo(chat_id, msg.photo[0].file_id)
    else:
        if debug:
            updater.bot.send_message(chat_id, msg.to_json())


def message_listener(bot, update):
    try:
        msg = update.message
        is_private = msg.chat.type == 'private'

        if not is_private:
            return

        forward_message(msg, FKXXX_ID)

    except Exception as e:
        return


updater = Updater(TOKEN)

updater.dispatcher.add_handler(MessageHandler(Filters.all, message_listener))

updater.start_polling()
updater.idle()
