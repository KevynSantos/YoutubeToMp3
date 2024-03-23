#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import asyncio
import datetime
import logging
import os
import subprocess
import tempfile

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def convert(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    link = message.split('/convert ')[1]
    await update.message.reply_text('Iniciando Download...')

    with tempfile.TemporaryDirectory() as temp_dir:
        output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")
        comando = ['yt-dlp', '-i', '--extract-audio', '--audio-format', 'mp3', '--socket-timeout', '60', link, '-o', output_template]

        # Execute o comando sem decodificar automaticamente a saída
        processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = processo.communicate()

        # Decodifica a saída manualmente usando UTF-8
        if processo.returncode != 0:
            erro = stderr.decode('utf-8')
            await update.message.reply_text(f"Houve algum problema durante o processamento: {erro}")
            return

        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                with open(file_path, 'rb') as audio_file:
                    await update.message.reply_audio(audio=audio_file, title="Download")
                await update.message.reply_text('Envio concluído.')
            except Exception as e:
                error_message = str(e)
                if "Timed out" in error_message:
                    await update.message.reply_text(
                        'O envio do arquivo excedeu o tempo limite. Por favor, aguarde cerca de 2-3 minutos para recebê-lo ou tente novamente.')
                else:
                    await update.message.reply_text(
                        f'Erro ao enviar o arquivo: {error_message}. Tente novamente mais tarde.')


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5247092979:AAHow1Mtj1Ngh3dKp2Qdgi_YXYb9FYh4LTE").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("convert", convert))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
