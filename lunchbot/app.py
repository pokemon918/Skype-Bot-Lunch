"""
Lunch Skype Bot

A simple Skype bot helps to choose restaurant for lunch.

:copyright: (c) 2017 by Serhii Shvorob.
:license: MIT, see LICENSE for more details.
"""
import json
import time

import requests
from flask import Flask, request

from .bot import BotDb, GREETING_RULE
from .utils import day_of_week_ukr


# Constants
EXPIRE_GAP = 30  # sec

app = Flask('lunchbot')
app.config.from_envvar('LUNCHBOT_SETTINGS')


BOT_DB = None
TOKEN = {}
TOKEN_EXPIRES = 0


def get_bot_db():
    global BOT_DB
    if not BOT_DB:
        BOT_DB = BotDb(app.config['BOT_DB_FILE'])

    return BOT_DB


def request_token():
    payload = {
        'grant_type': 'client_credentials',
        'client_id': app.config['APP_ID'],
        'client_secret': app.config['APP_PASSWORD'],
        'scope': 'https://api.botframework.com/.default',
    }
    token = requests.post('https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token', data=payload).content
    app.logger.info('Downloaded token: %s', token)
    return json.loads(token)


def get_token():
    global TOKEN, TOKEN_EXPIRES
    if TOKEN_EXPIRES - EXPIRE_GAP < time.time():
        TOKEN = request_token()
        TOKEN_EXPIRES = time.time() + TOKEN['expires_in']
    return TOKEN


def get_context():
    return dict(day_of_week_ukr=day_of_week_ukr())


def process_message(message, context):
    try:
        bot_db = get_bot_db()
        responses = bot_db.query(message, context)
    except:
        app.logger.exception('Error on "%s" message processing:', message)
        responses = ["Ooops :( Something went wrong on server's side. Please try later."]
    return responses


@app.route('/bot', methods=['POST'])
def bot():
    token = get_token()

    activity = request.get_json()
    app.logger.info('Data: %s', activity)

    activity_type = activity['type']
    bot_response = None

    if activity_type == 'message':
        bot_response = process_message(activity['text'], get_context())
    elif activity_type == 'contactRelationUpdate':
        if activity['action'] == 'add':
            bot_response = process_message(GREETING_RULE, get_context())

    if not bot_response:
        return ''

    msg = {
        'type': 'message',
        'conversation': activity['conversation'],
        'from': activity['recipient'],
        'recipient': activity['from'],
        'replyToId': activity['id'],

        'locale': app.config['BOT_LOCALE'],

        'text': '\n\n'.join(bot_response),
    }

    url = '{serviceUrl}/v3/conversations/{conversation[id]}/activities/{id}'.format_map(activity)
    headers = {
        'Authorization': 'Bearer ' + token['access_token'],
        'Content-Type': 'application/json'
    }
    requests.post(url, headers=headers, data=json.dumps(msg))
    return ''
