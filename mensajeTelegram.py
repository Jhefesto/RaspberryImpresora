from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import requests
import re
# 817752267:AAF3cb3Lyv92QVbxqpUcw2IffeCtjSN3XP4

def yo(bot, update):
    chat = update.message.chat_id
    bot.send_message(chat_id=chat,text="mi id="+str(chat))

def main():
    updater = Updater('817752267:AAF3cb3Lyv92QVbxqpUcw2IffeCtjSN3XP4')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('yo',yo))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
