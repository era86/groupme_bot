import os
import random
from flask import Flask, json, request
import requests

app = Flask(__name__)

# GROUP_ID
# BOT_ID
# GIPHY_RATING
# GIPHY_TOKEN

def verify_groupme_message(json_body):
    return json_body['group_id'] == os.getenv('GROUP_ID') and json_body['sender_type'] != 'bot'

def reply_to_groupme(message):
    payload = {
        'bot_id' : os.getenv('BOT_ID'),
        'text'   : message,
    }
    requests.post('https://api.groupme.com/v3/bots/post', json=payload)

def get_giphy_url(query=''):
    giphy_token = os.getenv('GIPHY_TOKEN')
    giphy_rating = os.getenv('GIPHY_RATING') or 'y'

    url = "http://api.giphy.com/v1/gifs/search?q='{query}'&api_key={token}&rating={rating}&limit=100".format(
        query=query,
        token=giphy_token,
        rating=giphy_rating
    )
    print("URL: {url}".format(url=url))

    response = requests.get(url)
    results = json.loads(response.text)

    idx = random.randint(0, 99)
    print("Index: {idx}".format(idx=idx))
    print("Results count: {count}".format(len(results['data'])))
    gif = results['data'][idx]
    return gif['images']['original']['url']

def get_reddit_url(sub):
    url = "https://www.reddit.com/r/{}.json".format(sub)
    print("URL: {url}".format(url=url))

    response = requests.get(url, headers={'User-agent': 'giphy-bot'})
    results = json.loads(response.text)

    link = results['data']['children'][random.randint(0, 25)]
    return link['data']['url']

@app.route('/', methods=['GET'])
def test_endpoint():
    query = request.args.get('q')
    return get_giphy_url(query)

@app.route('/', methods=['POST'])
def groupme_callback():
    json_body = request.get_json()

    giphy_cmds = {}
    for n in range(20):
        cmd = os.getenv('GIPHY_CMD_{}'.format(n))
        query = os.getenv('GIPHY_QUERY_{}'.format(n))

        if cmd:
            giphy_cmds[cmd] = query

    reddit_cmds = {}
    for n in range(20):
        cmd = os.getenv('REDDIT_CMD_{}'.format(n))
        sub = os.getenv('REDDIT_SUB_{}'.format(n))

        if cmd:
            reddit_cmds[cmd] = sub

    if verify_groupme_message(json_body):
        message = json_body['text']
        message_parts = message.split()

        if message_parts[0] == '/giphy':
            query = ' '.join(message_parts[1:])
            response = get_giphy_url(query)
            reply_to_groupme(response)
            return response

        if message_parts[0] == '/ohama':
            response = get_giphy_url('chive on')
            reply_to_groupme(response)

            response = get_giphy_url('chive on')
            reply_to_groupme(response)

            response = get_giphy_url('chive on')
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

        for cmd, query in giphy_cmds.items():
            if message_parts[0] == "/{}".format(cmd):
                response = get_giphy_url(query)
                reply_to_groupme(response)

        for cmd, sub in reddit_cmds.items():
            if message_parts[0] == "/{}".format(cmd):
                response = get_reddit_url(sub)
                reply_to_groupme(response)

    return 'No op'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
