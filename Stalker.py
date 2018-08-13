
from util import success, fail
import time
from Database import Database
import threading
db = Database('stories')

def extractData(story):
    """story = story.replace("'",'"')
    story = story.replace("False","false")
    story = story.replace("True","true")
    story = story.replace("None",'""')
    story = story.split('"video_dash_manifest"')[0][:-2]+'}]}'"""
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
            


class Stalker(object):
    def __init__(self, istance):
        self.pages = []
        self.pendingPages = []
        self.alivePages = []
        self.istance = istance
        pass
    def getStory(self, userid):
        self.istance.SendRequest('feed/user/' + str(userid) + '/reel_media/')
        return self.istance.LastJson

    def loadAllPages(self):
        self.pendingPages = [page for page in db.fetch('pages','','',True)]
        return success('Pages loaded: {}'.format(len(self.pendingPages)), data=self.pendingPages)
    
    def addPage(self, page):
        self.istance.searchUsername(page)
        if self.istance.LastJson['status'] == 'fail':
            return fail(self.istance.LastJson['message'])

        if db.fetch('pages','page',page) != None:
            return fail('Page {} already registered!'.format(page))
        data = {
            'page': page,
            'stories': [],
            'created_at': str(time.time()),
            'userid': self.istance.LastJson['user']['pk']
        }
        if db.save('pages', data):
            self.pendingPages.append(page)
            return success('Page {} registered'.format(page))
        return fail('Page {} not registered cause database error'.format(page))
        
    def startStalking(self):                   
        if len(self.pendingPages) == 0:
            return
        print(self.pendingPages)
        page = self.pendingPages.pop()   
         
        threading.Thread(target=self.stalk, args=(page,)).start()
            

    def stalk(self, page):
        pageName = page['page']
        print('Starting {} thread now'.format(pageName))
        self.alivePages.append(page)
        print(self.pendingPages)
        while True:
            print('Monitoring {} now...'.format(pageName))
            story = self.getStory(page['userid'])
            with open('story','w') as target:
                target.write(str(story))
            data = extractData(story)
            if data != []:
                stories = [story for story in db.fetch('pages', 'page', pageName)['stories']]
                storiesId = [story['id'] for story in stories]
                for d in data:
                    if d['id'] not in storiesId:
                        db.append('pages','page',pageName,'stories', d)
            time.sleep(10)