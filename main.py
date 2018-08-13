from InstagramAPI import InstagramAPI
import pickle
from Stalker import Stalker
username = ''
password = ''
def getStory(account, userid):
    account.SendRequest('feed/user/' + str(userid) + '/reel_media/')
#account = InstagramAPI(username, password)
#account.login()
"""if account.LastJson['status'] == 'fail':
    print('Cannot login')
"""
account = pickle.load(open('acc','rb'))
#pickle.dump(account, open('acc','wb'))
"""
user = ''
account.searchUsername(user)
userid = account.LastJson['user']['pk']
print(getStory(account, userid))"""

a = Stalker(account)
a.addPage('vinzfile')
a.loadAllPages()
a.startStalking()
