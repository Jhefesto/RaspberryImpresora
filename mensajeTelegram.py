from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import requests
import re


def yo(bot, update):
    chat = update.message.chat_id
    bot.send_message(chat_id=chat,text="mi id="+str(chat))

def main():
    updater = Updater('TOKENtelegramm')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('yo',yo))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
