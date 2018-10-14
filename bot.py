import os
import random
from flask import Flask, json, request
import requests
import datetime
import pytz

app = Flask(__name__)

def verify_groupme_message(json_body):
    return json_body['group_id'] == os.getenv('GROUP_ID') and json_body['sender_type'] != 'bot'

def reply_to_groupme(message):
    payload = {
        'bot_id' : os.getenv('BOT_ID'),
        'text'   : message,
    }
    requests.post('https://api.groupme.com/v3/bots/post', json=payload)

def get_rating():
    env_rating = os.getenv('GIPHY_RATING')
    if env_rating:
        return env_rating

    now = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
    if now.weekday() > 4:
        return 'r'
    else:
        if now.hour < 9 or now.hour >= 17:
            return 'r'

    return 'y'

def get_giphy_url(query=''):
    giphy_token = os.getenv('GIPHY_TOKEN')
    giphy_rating = get_rating()
    giphy_url = "http://api.giphy.com/v1/gifs/search?q='%s'&api_key=%s&rating=%s&limit=100" % (query, giphy_token, giphy_rating)
    response = requests.get(giphy_url)
    results = json.loads(response.text)

    gif = results['data'][random.randint(0, 99)]
    return gif['images']['original']['url']

def get_nsfw_url():
    env_nsfw_url = os.getenv('NSFW_URL')
    if env_nsfw_url:
        nsfw_url = env_nsfw_url
    else:
        nsfw_url = "https://www.reddit.com/r/NSFW_GIF.json"

    response = requests.get(nsfw_url, headers={'User-agent': 'giphy-bot'})
    results = json.loads(response.text)

    gif = results['data']['children'][random.randint(0, 25)]
    return gif['data']['url']

def nsfw_allowed(json_body):
    env_nsfw = os.getenv('NSFW') == 'yes'
    env_all_power = os.getenv('NSFW_ALL_POWER') == 'yes'

    if not env_nsfw:
        return False

    if not env_all_power and not json_body['name'] == 'Fred':
        return False

    if json_body['name'] == 'Fred':
        return True

    now = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
    if now.weekday() > 4:
        return True
    else:
        if now.hour < 9 or now.hour >= 17:
            return True

    return False


@app.route('/', methods=['GET'])
def test_endpoint():
    query = request.args.get('q')
    return get_giphy_url(query)

@app.route('/', methods=['POST'])
def groupme_callback():
    json_body = request.get_json()

    if verify_groupme_message(json_body):
        message = json_body['text']
        message_parts = message.split()

        if message_parts[0] == '/giphy':
            query = ' '.join(message_parts[1:])
            response = get_giphy_url(query)
            reply_to_groupme(response)
            return response

        if message_parts[0] == '/omaha':
            response = get_giphy_url('puppies')
            reply_to_groupme(response)

            response = get_giphy_url('puppies')
            reply_to_groupme(response)

            response = get_giphy_url('puppies')
            reply_to_groupme(response)

            return response

        if message_parts[0] == '/thermonuclear' and nsfw_allowed(json_body):
            response = get_nsfw_url()
            reply_to_groupme(response)


    return 'No op'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port, debug=True)
    app.run(host='0.0.0.0', port=port)
