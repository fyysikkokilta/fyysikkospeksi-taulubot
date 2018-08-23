# ===========================================================
# >> IMPORTS
# ===========================================================

# Python
import sys
import time

# Third-party
import telepot

from selenium import webdriver


# ===========================================================
# >> FUNCTIONS
# ===========================================================
def message_handler(msg):
    if msg['text'].startswith('/norppa'):

        # TODO better and lighter method should be implemented
        driver = webdriver.Chrome()
        driver.set_window_size(1024, 600)
        driver.get('http://cloudplayer.pukkistream.net/wwf_norppa')
        time.sleep(5)
        driver.save_screenshot('norppa.png')
        driver.close()
        img = open('norppa.png', 'rb')
        bot.sendPhoto(msg['chat']['id'], img)
        img.close()


# ===========================================================
# >> MAIN
# ===========================================================

# Get the token as sys arg
TOKEN = sys.argv[1]

bot = telepot.Bot(TOKEN)
bot.message_loop(message_handler)

# Keep the program running.
while 1:
    time.sleep(10)
