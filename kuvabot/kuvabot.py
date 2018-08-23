import json
import time

import requests
import telepot
from PIL import Image
from StringIO import StringIO

commands = ['/get']


# Main handler
def message_handler(msg):
    text = msg['text']
    # Look for specific command only
    if text.split(' ')[0] in commands and len(text.split(' ')) > 1:
        searh_term = ' '.join(text.split(' ')[1:]).strip().lower()
        img_url = get_image_url(searh_term)
        bot.sendPhoto(
            msg['chat']['id'],
            img_url,
            reply_to_message_id=msg['message_id']
        )


def get_image_url(search_term):
    start_index = '1'
    key = '?'
    cx = '?'
    search_url = "https://www.googleapis.com/customsearch/v1?q=" + \
        search_term + "&start=" + start_index + "&key=" + key + "&cx=" + cx + \
        "&searchType=image"
    r = requests.get(search_url)
    response = r.content.decode('utf-8')
    result = json.loads(response)

    images = result.get('items', None)
    image = images[0] if len(images) > 0 else None
    if image:
        url = image['link']
        return url
    return None


bot = telepot.Bot('?')
bot.message_loop(message_handler)

# Keep the program running.
while 1:
    time.sleep(10)
