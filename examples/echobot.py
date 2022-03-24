#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from __future__ import unicode_literals

import logging
import os
import subprocess
import sys
from io import StringIO, BytesIO
import fileinput

import pydub
import youtube_dl

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Oi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def convert(update: Update, _: CallbackContext) -> None:
    message = update['message']['text']
    link = message.split('/convert ')[1];
    print("Link:"+link);
    update.message.reply_text('Iniciando Download e Conversão...')

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=False)
                video_title = info_dict.get('title', None)
                id = info_dict.get('id',None)

        subprocess.check_output('youtube-dl -i --extract-audio --audio-format mp3 '+link, shell=True);

        nameFile = video_title.replace("/", "_") + "-" + id + '.mp3'

        update.message.reply_text('Arquivo Baixado')

        path = sys.path[0]+"\\"+nameFile

        waiting = True
        update.message.reply_text('Em preparação')
        while(waiting):
            if(os.path.exists(path)):
                update.message.reply_audio(audio=open(file=path,mode='rb'), title=nameFile)
                update.message.reply_text('Conversão concluída')
                waiting = False
    except:
        messageErrror = "Houve algum problema durante o processamento"
        update.message.reply_text(messageErrror)
    finally:
        if (os.path.exists(path)):
            try:
                os.remove(path)
            except(PermissionError):
                messageErrror = "Erro, por favor tente converter novamente. Caso tenha recebido o arquivo, ignore essa mensagem."
                update.message.reply_text(messageErrror)


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("5247092979:AAHow1Mtj1Ngh3dKp2Qdgi_YXYb9FYh4LTE")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("convert", convert))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
