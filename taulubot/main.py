import logging
import os
from io import BytesIO
from random import randint

import requests
from PIL import Image
from telegram.ext import Updater, CommandHandler

from taulubot.filter import colorize

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # workdir to __file__ location

frame = Image.open('images/frame.png', 'r')
frame_above = Image.open('images/frame_above.png', 'r')

# Enable logging
logging.basicConfig(
    filename='taulubot.log',
    filemode='a',
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
    if query.total_count == 0:
        return update.message.reply_text('Teillä ei ole profiilikuvaa tai olet asettanut' +
            ' sen näkyväksi vain kontakteille!'
        )
    photo = query.photos[0][-1].get_file()
    url = photo.file_path

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    _frame = frame
    _frame_above = colorize(frame_above, randint(0, 360))

    for f in [_frame, _frame_above]:
        f = f.resize(img.size)
        img.paste(f, (0, 0), f)
    filename = f'images/img_{user_id}.png'
    img.save(filename, format='PNG')

    with open(filename, 'rb') as f:
        context.bot.send_photo(chat_id, f)
    return os.remove(filename)


def help_handle(update, context):  # pylint: disable=unused-argument
    """Send info on /help"""
    update.message.reply_text("Lisää profiilikuvallesi kehys lähettämällä /taulu\n\n" +
        'Tietoa Fyysikkospeksistä löydät osoitteesta fyysikkospeksi.fi',
    )


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    token = os.environ['TAULUBOT_TOKEN']
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler(("taulu", "start"), taulu))
    dp.add_handler(CommandHandler("help", help_handle))

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
