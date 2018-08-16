#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from Stalker import Stalker
import json
from util import loadSession
with open('config.json','r') as target:
    config = json.loads(target.read())


result = loadSession()
if result['success'] == False:
    print('Please run main.py before and be sure `session.pkl` file is created')
    exit()

session = result['data']

s = Stalker(session)
s.loadAllPages()
s.startStalking()

    


def start(bot, update):
    update.message.reply_text('Go /help for commands')


def help(bot, update):
    update.message.reply_text('Commands available:\n\
/monitor pagename - Start to monitor a page\n\
/remove pagename - Remove a page\n\
/status - List all monitored pages')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    #logger.warning('Update "%s" caused error "%s"', update, error)

def monitor(bot, update, args):
    if len(args) == 0:
        update.message.reply_text('Invalid syntax. Please send me the page name')
        return
    pageName = args[0]
    result = s.addPage(pageName, update.message.from_user.id)
    if result['success'] == False:
        update.message.reply_text(result['message'])
        return
    update.message.reply_text(result['message'])
    s.startStalking()
def remove(bot, update, args):
    if len(args) == 0:
        update.message.reply_text('Invalid syntax. Please send me the page name')
        return
    pageName = args[0]
    result = s.removePage(pageName)
    if result['success'] == False:
        update.message.reply_text('Page {}. {}'.format(pageName, result['message']))
        return
    update.message.reply_text(result['message'])

def listAll(bot, update):
    pages = s.getAlivePages()
    msg = ''
    for p in pages:
        msg += 'Page: {}\n'.format(p)
    update.message.reply_text(msg)
def main():
    """Start the bot."""
    updater = Updater(config["token"])
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("monitor", monitor, pass_args=True))
    dp.add_handler(CommandHandler("remove", remove, pass_args=True))
    dp.add_handler(CommandHandler("list", listAll))
    dp.add_handler(CommandHandler("help", help))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
