# Instagram story stalker

Instagram story stalker is a tool which notifies you with a message on telegram whenever someone of your contacts adds a story.
### But why?
Mmh, I don't know. Fun, maybe?

## Getting started
You need to install and run MongoDB (`mongod`) and create config.json file.
The config.json file has the following syntax:
```
{
    "token": "608599861:AAHrLZVOXeKr48k5qSPN9N-ChXy3Fhr2-KQ",
    "adminId": "48968121",
    "instance": {
        "username": "",
        "password": ""
    }
}
```
`adminId` is the chat_id of the conversation on Telegram that you want to send to.

In order to install this script, you need to run:
```
$ pip3 install requests InstagramAPI pymongo
$ python3 main.py
```

## How does it work?
Actually there isn't a full control with telegram. It will be improved.
You can add pages after confirming login by:
```python
obj = Stalker(account)
# obj.addPage("pageName")
obj.loadAllPages()
obj.startStalking()
```
You only need to add each page to stalk manually once.

# TODO

- [x] Adding accounts with telegram
- [x] Removing accounts with telegram
- [ ] Rewrite lite InstagramAPI for stories
- [ ] Handle other errors


## It's a beta, It'll be improved :)
Enjoy