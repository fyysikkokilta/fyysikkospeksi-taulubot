import time
import requests
import re
import json
import os

import telepot
from lxml import html, etree

TOKEN = os.environ['VAALILAKANA_TOKEN']
BASE_URL = 'https://www.fyysikkokilta.fi/fiirumi'
TOPIC_LIST_URL = '{0}/viewforum.php?f=5'.format(BASE_URL)
VAALILAKANA_TOPIC_URL = '{0}/viewtopic.php?f=5&t=367'.format(BASE_URL)


def add_topic(title, link):
    with open('old_topics.txt', 'a') as f:
        f.write('{}\n'.format(link))
    broadcast_message(
        "Uusi postaus Vaalipeli-palstalla!\n\n*{0}*\n{1}".format(
            title,
            BASE_URL + link
        )
    )


def parse_link(topic):
    href = topic.attrib['href']
    return re.findall('.(.*f=.*)&', href)[0]


def broadcast_message(message, jauhis=False):
    print('Broadcasting message to: {}'.format(message))
    for channel in broadcast_channels:
        time.sleep(1)
        if jauhis:
            with open('jauhis.png', 'rb') as f:
                bot.sendSticker(channel, f)
            time.sleep(0.5)
        bot.sendMessage(channel, message, parse_mode='Markdown')


def parse_topics():
    try:
        page = requests.get(TOPIC_LIST_URL)
        tree = html.fromstring(page.content)
        topics = tree.xpath(
            '//*[@id="page-body"]/div[3]/div/ul[2]/li/dl/dt/div/a'
        )
    except Exception as e:
        print('ERROR: {}'.format(e))
        return
    old_topics = []
    with open('old_topics.txt', 'r') as f:
        for line in f:
            old_topics.append(line.replace('\n', ''))

    for topic in topics:
        link = parse_link(topic)
        if link not in old_topics:
            add_topic(topic.text, link)


lakana = {}
old_lakana = {}


def parse_online_vaalilakana(silent=False):
    try:
        page = requests.get(VAALILAKANA_TOPIC_URL)
        tree = html.fromstring(page.content)
        content = tree.xpath('//*[@id="post_content768"]/div')[0]
    except Exception as e:
        print('ERROR: {}'.format(e))
        return
    result = []
    for e in content:
        estr = etree.tostring(e).decode('utf-8')
        if e.text:
            result.append(e.text)
        else:
            # HACK: not decoding characters from all strings, replace instead
            row = estr.replace("<br/>\n", '').replace('&#228;', 'ä').replace(
                '&#214;', 'ö').replace('&#246;', 'ö')
            if row:
                # SPECIAL CASE: headers
                if 'TOIMIHENKI' in row:
                    row = 'TOIMIHENKILÖKSI 2018'
                elif 'RAATIIN' in row:
                    row = 'RAATIIN 2018'
                elif 'font-weight: bold' in estr:
                    row = '*{}*'.format(e.text_content().replace('\n', ''))
                result.append(row)

    header = ''
    subheader = ''
    subsubheader = ''
    for i in result[1:]:
        if i == 'RAATIIN 2018' or i == 'TOIMIHENKILÖKSI 2018':
            header = i
            continue
        if i[-1] == ':':
            subsubheader = i
            continue
        if i.isupper():
            subheader = i
            continue
        if not lakana.get(header, False):
            lakana[header] = {}
        if not lakana[header].get(subheader, False):
            lakana[header][subheader] = {}
        if not lakana[header][subheader].get(subsubheader, False):
            lakana[header][subheader][subsubheader] = []
        if not i in lakana[header][subheader][subsubheader]:
            lakana[header][subheader][subsubheader].append(i)
            old = old_lakana.get(header, {}).get(
                subheader, {}).get(subsubheader, [])
            if (i not in old and i.replace('*', '') not in old and not silent):
                broadcast_message(
                    'Uusi nimi vaalilakanassa!\n*{0}* {1}'.format(
                        subsubheader, i
                    ),
                    jauhis=True
                )
    # Update lakana
    with open('lakana.txt', 'w') as f:
        f.write(json.dumps(lakana))


def lakana_string():
    lakana_string = ''
    for h1 in sorted(lakana.keys()):
        if h1 != 'RAATIIN 2018':
            continue
        # lakana_string += '*{}*\n\n'.format(h1)
        for h2 in sorted(lakana[h1].keys()):
            # lakana_string += '*{}*\n\n'.format(h2)
            for h3 in sorted(lakana[h1][h2].keys()):
                lakana_string += '*{}*\n'.format(h3)
                lakana_string += '\n'.join(lakana[h1][h2][h3]) + '\n\n'

    return lakana_string

broadcast_channels = []


def add_channel(chat_id):
    broadcast_channels.append(chat_id)
    with open('channels.txt', 'a') as f:
        f.write('{}\n'.format(chat_id))
    print('Added channel: {}'.format(chat_id))


def message_handler(msg):
    text = msg.get('text', '')
    if '/activate' in text:
        chat = msg.get('chat', '')
        if chat:
            chat_id = chat.get('id', '')
            if chat_id and str(chat_id) not in broadcast_channels:
                sender = msg.get('from', '')
                if sender:
                    print('Command /activate from {}'.format(sender))
                add_channel(chat_id)
                bot.sendMessage(
                    chat_id,
                    'Onnistuneesti rekisteröity tiedotuskanavaksi!',
                    reply_to_message_id=msg.get('message_id', ''),
                    parse_mode='Markdown'
                )
    elif '/lakana' in text:
        chat = msg.get('chat', '')
        if chat and chat.get('id', ''):
            sender = msg.get('from', '')
            if sender:
                print('Command /lakana from {}'.format(sender))
            bot.sendMessage(
                chat.get('id', ''),
                lakana_string(),
                parse_mode='Markdown'
                # reply_to_message_id=msg.get('message_id', '')
            )

    elif '/jauhis' in text:
        chat = msg.get('chat', '')
        if chat:
            sender = msg.get('from', '')
            if sender:
                print('Command /jauhis from {}'.format(sender))
            with open('jauhis.png', 'rb') as img:
                bot.sendSticker(chat.get('id', ''), img)


bot = telepot.Bot(TOKEN)
bot.message_loop(message_handler)

with open('channels.txt', 'r') as f:
    for line in f:
        c = line.replace('\n', '')
        chat = bot.getChat(c)
        print(chat)
        if c not in broadcast_channels:
            broadcast_channels.append(c)

with open('lakana.txt', 'r') as f:
    data = f.read()
    if data:
        old_lakana = json.loads(data)

parse_online_vaalilakana(silent=True)


print('Loaded channels: {}'.format(str(broadcast_channels)))

if old_lakana != lakana:
    # broadcast_message(
    #     'Vaalilakana on päivittynyt!\n\n{}'.format(lakana_string())
    # )
    # print('Broadcasting lakana update')
    with open('lakana.txt', 'w') as f:
        f.write(json.dumps(lakana))

# Keep the program running.
while 1:
    time.sleep(30)
    try:
        parse_topics()
        parse_online_vaalilakana()
    except:
        continue
