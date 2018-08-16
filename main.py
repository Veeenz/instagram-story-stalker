from InstagramAPI import InstagramAPI
import pickle
from Stalker import Stalker
import json
with open('config.json') as target:
    config = json.loads(target)
username = config['instance']['username']
password = config['instance']['username']
account = InstagramAPI(username, password)
account.login()
if account.LastJson['status'] == 'fail':
    print('Cannot login, {}'.format(account.LastJson['message']))
else:
    
    with open('session.pkl', 'wb') as target:
        pickle.dump(account, target)