#!/usr/bin/python
# -*- coding: utf-8 -*-

# ===========================================================
# >> IMPORTS
# ===========================================================

# Python
import os
import time
import json

# Third-party
import telepot
import requests

from PIL import Image
from StringIO import StringIO

from bs4 import BeautifulSoup


# ===========================================================
# >> FUNCTIONS
# ===========================================================

# Simple logger
log_dir = './log'
log_file = '/log.txt'
log_path = log_dir + log_file

if not os.path.isdir(log_dir):
    os.makedirs(log_dir)

if not os.path.exists(log_path):
    log_file = open(log_path, 'w')
    log_file.close()


def simple_log(entry):
    log_file = open(log_path, 'a')
    log_file.write('\n[{0}] {1}'.format(
        time.strftime('%d-%m-%Y %H:%M:%S', time.localtime()),
        entry
    ))
    log_file.close()

# Decorator
abbreviation_methods = list()


def abbreviation_method(func):
    """ Decorate different abbreviation methods for easy extending """
    global abbreviation_methods
    abbreviation_methods.append(func)
    return func


# Abbreviation methods
@abbreviation_method
def get_answer_urbaani_sanakirja(phrase):
    """ Look up the phrase from www.urbaanisanakirja.com (Finnish) """

    # Format the query by replacing spaces and common special letters
    phrase = phrase.replace(' ', '-').replace(u'ä', 'a').replace(u'ö', 'o')

    response = requests.get(
        u'https://www.urbaanisanakirja.com/word/{}/'.format(phrase)
    )

    # Try to parse the answer and example from the response
    soup = BeautifulSoup(response.text, 'html.parser')
    boxes = soup.find_all('div', class_='box')

    if not boxes:
        return '', ''
    box = boxes[0]

    meanings = box.find_all('p')
    examples = box.find_all('blockquote')

    meaning = meanings[0].text.strip() if meanings else ''
    example = examples[0].text.strip() if examples else ''

    return meaning, example


@abbreviation_method
def get_answer_urban_dictionary(phrase):
    """ Look up the phrase from www.urbandictionary.com """

    # Format the query by replacing spaces
    phrase = phrase.replace(' ', '%20')

    response = requests.get(
        u'http://www.urbandictionary.com/define.php?term={}'.format(phrase)
    )

    # Try to parse the answer and example from the response
    soup = BeautifulSoup(response.text, 'html.parser')

    meanings = soup.find_all('div', class_='meaning')
    examples = soup.find_all('div', class_='example')

    meaning = meanings[0].text.strip() if meanings else ''
    example = examples[0].text.strip() if examples else ''

    return meaning, example


def get_image(search_term):
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
        link = image['link']
        return link
        img_r = requests.get(link)
        title = search_term.replace('/', '').replace('\\', '')
        img_file = open('{}.jpg'.format(title), 'w')
        try:
            Image.open(StringIO(img_r.content)).save(img_file, 'JPEG')
        except IOError as e:
            # Throw away some gifs
            print('ERROR: Could not save: {0}; {1}'.format(link, e))
        finally:
            return img_file
        return None


# Main handler
def message_handler(msg):
    """ Handler for listening Telegram commands and performing actions """

    try:
        text = msg['text']
        simple_log(str(msg))

        if text in info_commands:
            reply = (
                'ZYXMegaBot palveluksessanne! Tuetut komennot:\n'
                '/info - tuottaa tämän viestin\n'
                '/lsb <parametri> - hakee selityksen parametrina '
                'annetulle sanalle tai lauseelle\n'
                '/get <parametri> - hakee kuvan parametrina '
                'annetulla hakusanalla'
            )
            bot.sendMessage(
                msg['chat']['id'],
                reply,
                reply_to_message_id=msg['message_id']
            )

        if text.split(' ')[0] in img_commands and len(text.split(' ')) > 1:
            searh_term = ' '.join(text.split(' ')[1:]).strip().lower()
            img_file = get_image(searh_term)
            bot.sendPhoto(
                msg['chat']['id'],
                img_file,
                reply_to_message_id=msg['message_id']
            )

        # Look for specific command only
        if text.split(' ')[0] in lsb_commands and len(text.split(' ')) > 1:
            search_phrase = ' '.join(text.split(' ')[1:]).strip().lower()

            if search_phrase == 'lsb':
                reply = (
                    'Lyhenteet selittävä botti eli LSB selittää sille' +
                    'annetut lyhenteet.\n\n"\lsb lsb"'
                )
                bot.sendMessage(
                    msg['chat']['id'],
                    reply,
                    reply_to_message_id=msg['message_id']
                )
                return

            # Try to find the explanation
            answer = example = ''
            for abbr_method in abbreviation_methods:
                answer, example = abbr_method(search_phrase)
                if answer:
                    break
            else:
                # If no explanation was found send 'not found' and abort
                bot.sendMessage(
                    msg['chat']['id'],
                    u'Lyhennettä ei löydy',
                    reply_to_message_id=msg['message_id']
                )
                return

            # Reply to command with the answer and possible example
            reply = answer + ('\n\n"' + example + '"' if example else '')
            bot.sendMessage(
                msg['chat']['id'],
                reply,
                reply_to_message_id=msg['message_id']
            )
    except Exception as e:
        simple_log(str(e) + str(msg))


# ===========================================================
# >> MAIN
# ===========================================================

# Secret token (unique, get your own from BotFather!)
token = '?'

# Commands for using the bot
lsb_commands = ['/lyhenne', '/lsb']
img_commands = ['/get']
info_commands = ['/info']

# Initialize the bot and attach the command listener
bot = telepot.Bot(token)
bot.message_loop(message_handler)

# Keep the program running.
while 1:
    time.sleep(10)
