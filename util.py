def success(msg, data=''):
    return {'success': True, 'message':msg, 'data':data}

def fail(msg):
    return {'success': False, 'message': msg}

def notify(msg, chatid):
    import requests, json
    with open('config.json', 'r') as target:
        config = json.loads(target.read())
    token = config["token"]
    sendMessageUrl = 'https://api.telegram.org/bot{}/sendMessage?text={}&chat_id={}'
    req = requests.get(sendMessageUrl.format(token, msg, chatid), timeout=3)
    return req