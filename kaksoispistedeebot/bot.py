from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
import sqlite3
import traceback
import schedule
import time

conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS posts
        (
            chat_id text,
            chat_name text,
            message_id text,
            date text,
            user_id text,
            username text,
            count integer
        )
""")
c.execute("""
    CREATE TABLE IF NOT EXISTS voters
        (
            chat_id text,
            chat_name text,
            user_id text,
            username text,
            count integer
        )
""")
conn.commit()

last_messages = {}


def __get_points(cursor, table_name, identifiers):
    cursor.execute(
        'SELECT count FROM {} WHERE {}'.format(
            table_name, ' AND '.join([field + '=?' for field in identifiers])
        ),
        tuple(identifiers.values())
    )
    res = cursor.fetchone()
    count = res[0] if res else 0
    return count


def __update_points(cursor, table_name, exists, data, identifiers, count):
    if exists:
        cursor.execute(
            'UPDATE {} SET count=? WHERE {}'.format(
                table_name,
                ' AND '.join([field + '=?' for field in identifiers.keys()])
            ),
            (count, ) + tuple(identifiers.values())
        )
    else:
        cursor.execute(
            'INSERT INTO {} VALUES ({})'.format(
                table_name, ','.join(['?']*len(data))
            ),
            data
        )


def add_point(bot, update):
    try:
        # print(update.message.reply_to_message)
        chat_id = update.message.chat.id
        chat_name = update.message.chat.title

        if update.message.reply_to_message:
            user = update.message.reply_to_message.from_user
            message_id = update.message.reply_to_message.message_id
            date = update.message.reply_to_message.date
        elif chat_id in last_messages:
            user = last_messages[chat_id].from_user
            message_id = last_messages[chat_id].message_id
            date = last_messages[chat_id].date
        else:
            return
        
        voter = update.message.from_user

        # Can't give points to self
        if voter.id == user.id:
            return

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        points = __get_points(
            c,
            'posts',
            {'chat_id': chat_id, 'user_id': user.id, 'message_id': message_id}
        )
        __update_points(
            c,
            'posts',
            bool(points),
            (
                chat_id,
                chat_name,
                message_id,
                date,
                user.id,
                user.username,
                points + 1
            ),
            {
                'chat_id': chat_id,
                'user_id': user.id,
                'message_id': message_id
            },
            points + 1
        )

        votes = __get_points(
            c,
            'voters',
            {'chat_id': chat_id, 'user_id': voter.id}
        )
        __update_points(
            c,
            'voters',
            bool(votes),
            (chat_id, chat_name, voter.id, voter.username, votes + 1),
            {'chat_id': chat_id, 'user_id': voter.id},
            votes + 1
        )

        conn.commit()
        conn.close()

    except Exception as e:
        traceback.print_exc()


def top_scorers(chat_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        """SELECT username, SUM(count) FROM posts
            WHERE chat_id=? GROUP BY user_id ORDER BY SUM(count) DESC""",
        (chat_id, )
    )
    res = c.fetchall()
    conn.close()

    s = 'TOP 10 :D-scorers\n'
    for i, u in enumerate(res[:10]):
        s += '{}. {} - {}\n'.format(i + 1, u[0], u[1])

    return s


def top_voters(chat_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        """SELECT username, SUM(count) FROM voters
            WHERE chat_id=? GROUP BY user_id ORDER BY SUM(count) DESC""",
        (chat_id, )
    )
    res = c.fetchall()
    conn.close()

    s = 'TOP 10 :D-voters\n'
    for i, u in enumerate(res[:10]):
        s += '{}. {} - {}\n'.format(i + 1, u[0], u[1])

    return s


def cmd_top_scorers(bot, update):
    try:
        chat_id = update.message.chat.id
        update.message.reply_text(top_scorers(chat_id))
    except Exception as e:
        traceback.print_exc()


def cmd_top_voters(bot, update):
    try:
        chat_id = update.message.chat.id
        update.message.reply_text(top_voters(chat_id))
    except Exception as e:
        traceback.print_exc()


def cmd_user_rank(bot, update):
    try:
        chat_id = update.message.chat.id
        user_id = update.message.from_user.id
        username = update.message.from_user.username
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute(
            """SELECT user_id, SUM(count) FROM posts
                WHERE chat_id=? GROUP BY user_id ORDER BY SUM(count) DESC""",
            (chat_id, )
        )
        res = c.fetchall()
        me = next((user for user in res if user[0] == str(user_id)), ())
        if not me:
            update.message.reply_text("You haven't been ranked yet.")
            return
        ranking = res.index(me) + 1
        conn.close()
        update.message.reply_text(
            'Rank {}/{}: {} - {}'.format(
                ranking, len(res), username, me[1]
            )
        )
    except Exception as e:
        traceback.print_exc()


def cmd_private_rank(bot, update):
    try:
        chat_id = update.message.chat.id
        user_id = update.message.from_user.id
        username = update.message.from_user.username
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute(
            """SELECT chat_name, SUM(count) FROM posts
                WHERE user_id=? GROUP BY chat_id ORDER BY SUM(count) DESC""",
            (user_id, )
        )
        res = c.fetchall()
        conn.close()
        s = '<b>YOUR :D-SCORES</b>\n'
        s += '\n'.join(['{} - {}'.format(g[0], g[1]) for g in res])
        update.message.reply_html(s)
    except Exception as e:
        traceback.print_exc()


def save_last_message(bot, update):
    try:
        chat_id = update.message.chat.id
        last_messages[chat_id] = update.message
    except Exception as e:
        traceback.print_exc()


def post_rankings(updater):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        """SELECT DISTINCT chat_id FROM posts"""
    )
    res = c.fetchall()
    for chat_id in res:
        scorers = top_scorers(chat_id[0])
        voters = top_voters(chat_id[0])
        updater.bot.send_message(
            chat_id[0],
            '<b>DAILY SUMMARY</b>\n{}\n{}'.format(scorers, voters),
            parse_mode='HTML'
        )


updater = Updater('')

updater.dispatcher.add_handler(
    MessageHandler(Filters.regex(':D$') & Filters.reply, add_point)
)
updater.dispatcher.add_handler(
    MessageHandler(Filters.regex('^[:]+[D]+$'), add_point)
)
updater.dispatcher.add_handler(MessageHandler(
    Filters.private & Filters.command & Filters.regex('rank$'),
    cmd_private_rank
))
# updater.dispatcher.add_handler(CommandHandler('top', cmd_top_scorers))
# updater.dispatcher.add_handler(CommandHandler('voters', cmd_top_voters))
# updater.dispatcher.add_handler(CommandHandler('rank', cmd_user_rank))
updater.dispatcher.add_handler(MessageHandler(Filters.all, save_last_message))

updater.start_polling()
# updater.idle()

schedule.every().day.at("00:00").do(post_rankings, updater)

while True:
    schedule.run_pending()
    time.sleep(60)
