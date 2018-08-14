from InstagramAPI import InstagramAPI
import pickle
from Stalker import Stalker
username = ''
password = ''
def getStory(account, userid):
    account.SendRequest('feed/user/' + str(userid) + '/reel_media/')
account = InstagramAPI(username, password)
account.login()


a = Stalker(account)
a.loadAllPages()
a.startStalking()
