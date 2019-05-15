
from util import success, fail, notify
import time
from Database import Database
import threading
import json

import logging
with open('config.json', 'r') as target:
        config = json.loads(target.read())
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(name)s: %(message)s"
    )
logger = logging.getLogger('STALKER')


db = Database('stories')

def extractStoryData(story):
    items = story['items']
    validVideoVersion = ''
    stories = []
    for item in items:
        if 'video_versions' in item:
            height = 0
            for video in item['video_versions']:
                if video['height'] > height:
                    validVideoVersion = video
                    height = video['height']
            data = {'type': 'video', 'id': str(item['pk']), 'url': validVideoVersion['url']}
        elif 'image_versions2' in item:
            height = 0
            for image in item['image_versions2']['candidates']:
                if image['height'] > height:
                    validImageVersion = image
                    height = image['height']
                data = {'type': 'image', 'id': str(item['pk']), 'url': validImageVersion['url']}
        stories.append(data)
    return stories

def extractPostData(post):
    items = post['items']
    posts = []
    for item in items:
        if (item['caption'] != None):
            if 'video_versions' in item:
                height = 0
                for video in item['video_versions']:
                    if video['height'] > height:
                        validVideoVersion = video
                        height = video['height']
                data = {'type': 'video', 'id': str(item['caption']['media_id']), 'url': validVideoVersion['url']}
                posts.append(data)
            elif 'image_versions2' in item:
                height = 0
                for image in item['image_versions2']['candidates']:
                    if image['height'] > height:
                        validImageVersion = image
                        height = image['height']
                    data = {'type': 'image', 'id': str(item['caption']['media_id']), 'url': validImageVersion['url']}
                posts.append(data)
    return posts

def parseStory(story, owner):
    return "New story of {}, it is a {}!\n\nDownload not available yet!\n\nUrl: {}".format(owner, story["type"], story["url"])
def parsePost(post, owner):
    return "New post of {}, it is a {}!\n\nDownload not available yet!\n\nUrl: {}".format(owner, post["type"], post["url"])

class Stalker(object):
    def __init__(self, istance):
        self.pages = []
        self.pendingPages = []
        self.alivePages = []
        self.deadPages = []
        self.istance = istance
        pass
    def getStory(self, userid):
        self.istance.SendRequest('feed/user/' + str(userid) + '/reel_media/')
        return self.istance.LastJson
    def getPost(self, userid):
        self.istance.getUserFeed(userid)
        return self.istance.LastJson

    def loadAllPages(self):
        self.pendingPages = [page for page in db.fetch('pages','','',True)]
        return success('Pages loaded: {}'.format(len(self.pendingPages)), data=self.pendingPages)
    
    def addPage(self, pageName, referenceId=''):
        self.istance.searchUsername(pageName)
        if self.istance.LastJson['status'] == 'fail':
            logger.error("There was an error while getting userid")
            notify('There was an error while getting userid', config["adminId"])
            return fail(self.istance.LastJson['message'])
        
        if db.fetch('pages','page',pageName) != None:
            return fail('Page {} already registered!'.format(pageName))
        data = {
            'page': pageName,
            'stories': [],
            'posts': [],
            'created_at': str(time.time()),
            'userid': str(self.istance.LastJson['user']['pk']),
            'referenceId': str(referenceId)
        }
        if db.save('pages', data):
            self.pendingPages.append(data)
            logger.info('Registered {}'.format(pageName))
            return success('Page {} registered'.format(pageName))
        return fail('Page {} not registered cause database error'.format(pageName))
        
    def removePage(self, pageName):
        if db.fetch('pages','page',pageName) == None:
            return success("Page {} wasn't monitored".format(pageName)) # it is anyway a success
        db.delete('pages', 'page', pageName)
        self.deadPages.append(pageName)
        if pageName in self.alivePages:
            self.alivePages.remove(pageName)
        else:
            logger.error('There was an error, {} was not in alivePages. It is a bug'.format(pageName))
        return success('Page {} removed'.format(pageName))
    def startStalking(self):                   
        while True:
            if len(self.pendingPages) == 0:
                return            
            page = self.pendingPages.pop()               
            threading.Thread(target=self.stalkStories, args=(page,)).start()
            threading.Thread(target=self.stalkPosts, args=(page,)).start()
    
    def getAlivePages(self):
        return self.alivePages

    def stalkStories(self, page):
        pageName = page['page']
        logger.debug('Starting {} thread now'.format(pageName))
        self.alivePages.append(pageName)
        
        while True:
            if pageName in self.deadPages:
                logger.debug('Closing stalk stories thread for account {}. It has been removed from stalking'.format(pageName))
                return #Close thread
            logger.debug('Monitoring stories of {} now...'.format(pageName))
            story = self.getStory(page['userid'])            
            data = extractStoryData(story)            
            if data != []:
                stories = [story for story in db.fetch('pages', 'page', pageName)['stories']]
                storiesId = [story['id'] for story in stories]
                for d in data:
                    if d['id'] not in storiesId:
                        logger.info('Story to add: {}'.format(d))
                        if page['referenceId'] == "":
                            logger.info("Cannot notify, referenceId is empty. I'm notifying it to admin (it is a debug feature, everyone must have a referenceId in future)")
                            notify(parseStory(d, pageName), config["adminId"])
                        else:
                            notify(parseStory(d, pageName), page['referenceId'])
                        db.append('pages','page',pageName,'stories', d)
            timeToSleep = 20
            logger.debug('[page:{}] Waiting {} seconds'.format(pageName, timeToSleep))
            time.sleep(timeToSleep)

    def stalkPosts(self, page):
        pageName = page['page']
        logger.debug('Starting {} thread now'.format(pageName))

        while True:
            if pageName in self.deadPages:
                logger.debug('Closing stalk posts thread for account {}. It has been removed from stalking'.format(pageName))
                return #Close thread
            logger.debug('Monitoring posts of {} now...'.format(pageName))
            post = self.getPost(page['userid'])
            data = extractPostData(post)
            if data != []:
                posts = [p for p in post['items'] for posts in db.fetch('pages', 'page', pageName)['posts']]
                posts_id = []
                for p in posts:
                    posts_id.append(p["id"].split("_")[0])
                # let's grab only first few
                data = data[:5]
                for d in data:
                    d['id'] = d['id'].split("_")[0]
                    if d['id'] not in posts_id:
                        logger.info('Post to add: {}'.format(d))
                        if page['referenceId'] == "":
                            logger.info("Cannot notify, referenceId is empty. I'm notifying it to admin (it is a debug feature, everyone must have a referenceId in future)")
                            notify(parsePost(d, pageName), config["adminId"])
                        else:
                            notify(parsePost(d, pageName), page['referenceId'])
                        db.append('pages','page',pageName,'posts', d)
            timeToSleep = 20
            logger.debug('[page:{}] Waiting {} seconds'.format(pageName, timeToSleep))
            time.sleep(timeToSleep)
