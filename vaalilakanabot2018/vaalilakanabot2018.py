import os
import re
import time
import json
import requests

from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from lxml import html, etree

TOKEN = os.environ['VAALILAKANABOT_TOKEN']
ADMIN_CHAT_ID = 103205934

BASE_URL = 'https://www.fyysikkokilta.fi/fiirumi'
TOPIC_LIST_URL = '{0}/viewforum.php?f=5'.format(BASE_URL)

channels = []
vaalilakana = {}
last_applicant = None
fiirumi_posts = []

with open('vaalilakana.json', 'r') as f:
    data = f.read()
    vaalilakana = json.loads(data)

print('Loaded vaalilakana: {}'.format(vaalilakana))

with open('channels.json', 'r') as f:
    data = f.read()
    channels = json.loads(data)

print('Loaded channels: {}'.format(channels))

with open('fiirumi_posts.json', 'r') as f:
    data = f.read()
    fiirumi_posts = json.loads(data)

print('Loaded fiirumi posts: {}'.format(fiirumi_posts))

updater = Updater(TOKEN)


def _save_data(filename, data):
    with open(filename, 'w') as f:
        f.write(json.dumps(data))


def _vaalilakana_to_string(vaalilakana):
    output = ''
    for position in vaalilakana:
        output += '<b>{position}</b>\n'.format(position=position)
        for applicant in vaalilakana[position]:
            link = applicant['fiirumi']
            if link:
                output += '<a href="{link}">{name}</a>\n'.format(
                    name=applicant['name'],
                    link=link
                )
            else:
                output += '{name}\n'.format(name=applicant['name'])

        output += '\n'
    return output


def _parse_fiirumi_posts():
    try:
        page = requests.get(TOPIC_LIST_URL)
        tree = html.fromstring(page.content)
        posts = tree.xpath(
            '//*[@id="page-body"]/div[3]/div/ul[2]/li/dl/dt/div/a'
        )
    except Exception as e:
        print('[ERROR]', e)
        return

    for post in posts:
        href = post.attrib['href']
        link = re.findall('.(.*f=.*)&', href)[0]
        if link not in fiirumi_posts:
            fiirumi_posts.append(link)
            _save_data('fiirumi_posts.json', fiirumi_posts)
            _announce_to_channels(
                '<b>Uusi postaus Vaalipeli-palstalla!</b>\n{name}\n{base}{link}'.format(
                    name=post.text,
                    base=BASE_URL,
                    link=link
                )
            )


def _announce_to_channels(message):
    for cid in channels:
        updater.bot.send_message(cid, message, parse_mode='HTML')


def remove_applicant(bot, update):
    try:
        chat_id = update.message.chat.id
        if chat_id == ADMIN_CHAT_ID:
            text = update.message.text.replace('/poista', '').strip()
            params = text.split(',')
            
            try:
                position = params[0].strip()
                name = params[1].strip()
            except:
                updater.bot.send_message(
                    chat_id,
                    'Virheelliset parametrit - /poista <virka>, <nimi>'
                )
                raise Exception('Invalid parameters')

            if position not in vaalilakana:
                updater.bot.send_message(
                    chat_id,
                    'Tunnistamaton virka: {}'.format(position),
                    parse_mode='HTML'
                )
                raise Exception('Unknown position {}'.format(position))
            
            found = None
            for applicant in vaalilakana[position]:
                if name == applicant['name']:
                    found = applicant
                    break

            if not found:
                updater.bot.send_message(
                    chat_id,
                    'Hakijaa ei löydy {}'.format(name),
                    parse_mode='HTML'
                )
                raise Exception('Apllicant not found: {}'.format(name))

            vaalilakana[position].remove(found)
            _save_data('vaalilakana.json', vaalilakana)
            global last_applicant
            last_applicant = None

            updater.bot.send_message(
                chat_id,
                'Poistettu:\n{position}: {name}'.format(
                    **found
                ),
                parse_mode='HTML'
            )
    except Exception as e:
        print('[ERROR]', e)


def add_fiirumi_to_applicant(bot, update):
    try:
        chat_id = update.message.chat.id
        if chat_id == ADMIN_CHAT_ID:
            text = update.message.text.replace('/lisaa_fiirumi', '').strip()
            params = text.split(',')
            
            try:
                position = params[0].strip()
                name = params[1].strip()
                fiirumi = params[2].strip()
            except:
                updater.bot.send_message(
                    chat_id,
                    'Virheelliset parametrit - /lisaa_fiirumi <virka>, <nimi>, <fiirumi>'
                )
                raise Exception('Invalid parameters')

            if position not in vaalilakana:
                updater.bot.send_message(
                    chat_id,
                    'Tunnistamaton virka: {}'.format(position),
                    parse_mode='HTML'
                )
                raise Exception('Unknown position {}'.format(position))
            
            found = None
            for applicant in vaalilakana[position]:
                if name == applicant['name']:
                    found = applicant
                    applicant['fiirumi'] = fiirumi
                    break

            if not found:
                updater.bot.send_message(
                    chat_id,
                    'Hakijaa ei löydy {}'.format(name),
                    parse_mode='HTML'
                )
                raise Exception('Apllicant not found: {}'.format(name))

            _save_data('vaalilakana.json', vaalilakana)
            global last_applicant
            last_applicant = None

            updater.bot.send_message(
                chat_id,
                'Lisätty Fiirumi:\n{position}: <a href="{fiirumi}">{name}</a>'.format(
                    fiirumi,
                    **found
                ),
                parse_mode='HTML'
            )
    except Exception as e:
        print('[ERROR]', e)


def add_applicant(bot, update):
    try:
        chat_id = update.message.chat.id
        if chat_id == ADMIN_CHAT_ID:
            text = update.message.text.replace('/lisaa', '').strip()
            params = text.split(',')
            
            try:
                position = params[0].strip()
                name = params[1].strip()
                fiirumi = ''
                if len(params) > 2:
                    fiirumi = params[2].strip()
            except:
                updater.bot.send_message(
                    chat_id,
                    'Virheelliset parametrit - /lisaa <virka>, <nimi>, [fiirumi]'
                )
                raise Exception('Invalid parameters')
            
            new_applicant = {
                'name': name,
                'position': position,
                'fiirumi': fiirumi
            }

            if position not in vaalilakana:
                updater.bot.send_message(
                    chat_id,
                    'Tunnistamaton virka: {}'.format(position),
                    parse_mode='HTML'
                )
                raise Exception('Unknown position {}'.format(position))

            vaalilakana[position].append(new_applicant)
            _save_data('vaalilakana.json', vaalilakana)
            global last_applicant
            last_applicant = new_applicant

            updater.bot.send_message(
                chat_id,
                'Lisätty:\n{position}: {name} ({fiirumi}).\n\nLähetä tiedote komennolla /tiedota'.format(
                    **new_applicant
                ),
                parse_mode='HTML'
            )

    except Exception as e:
        print('[ERROR]', e)


def show_vaalilakana(bot, update):
    try:
        chat_id = update.message.chat.id
        updater.bot.send_message(
            chat_id,
            _vaalilakana_to_string(vaalilakana),
            parse_mode='HTML'
        )
    except Exception as e:
        print('[ERROR]', e)


def register_channel(bot, update):
    try:
        chat_id = update.message.chat.id
        if chat_id not in channels:
            channels.append(chat_id)
            _save_data('channels.json', channels)
    except Exception as e:
        print('[ERROR]', e)


def announce_new_applicant(bot, update):
    try:
        chat_id = update.message.chat.id
        if chat_id == ADMIN_CHAT_ID:
            global last_applicant
            if last_applicant:
                _announce_to_channels(
                    '<b>Uusi nimi vaalilakanassa!</b>\n{position}: <i>{name}</i>'.format(
                        **last_applicant
                    )
                )
            last_applicant = None
    except Exception as e:
        print('[ERROR]', e)


def jauhis(bot, update):
    try:
        chat_id = update.message.chat.id
        with open('jauhis.png', 'rb') as jauhis:
            updater.bot.send_sticker(chat_id, jauhis)
    except Exception as e:
        print('[ERROR]', e)


updater.dispatcher.add_handler(CommandHandler('lisaa', add_applicant))
updater.dispatcher.add_handler(CommandHandler('lisaa_fiirumi', add_fiirumi_to_applicant))
updater.dispatcher.add_handler(CommandHandler('poista', remove_applicant))
updater.dispatcher.add_handler(CommandHandler('lakana', show_vaalilakana))
updater.dispatcher.add_handler(CommandHandler('tiedota', announce_new_applicant))
updater.dispatcher.add_handler(CommandHandler('start', register_channel))
updater.dispatcher.add_handler(CommandHandler('jauhis', jauhis))

updater.start_polling()
# updater.idle()

while True:
    _parse_fiirumi_posts()
    time.sleep(10)
