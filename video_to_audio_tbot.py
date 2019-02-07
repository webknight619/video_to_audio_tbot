import youtube_dl

from urllib.parse import urlparse

import os, sys
import asyncio
import telepot
import telepot.aio
from telepot.aio.loop import MessageLoop


def uri_validator(x):
    try:
        result = urlparse (x)
        return all ([result.scheme, result.netloc, result.path])
    except:
        return False


async def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance (msg)
    print ('Chat:', content_type, chat_type, chat_id)

    if content_type != 'text':
        return

    command = msg['text'][-1:].lower ()

    if command == 'c':
        await bot.sendMessage (chat_id, "puff")
    else:
        url = msg['text']
        if not uri_validator (url):
            await bot.sendMessage (chat_id, "please provide valid url")
            return

        options = {
            'format': 'worstaudio',
            # 'extractaudio': True,  # only keep the audio
            # 'audioformat': "m4a",  # convert to m4a
            'outtmpl': '%(id)s.%(ext)s',  # name the file the ID of the video
            'noplaylist': True,  # only download single song, not playlist
        }
        with youtube_dl.YoutubeDL (options) as ydl:
            await bot.sendMessage (chat_id, "Please wait till video will be downloaded and uploaded back to you)")

            info_dict = ydl.extract_info (url, download=True)
            title = info_dict.get ('title', None)
            id = info_dict.get ('id', None)
            ext = info_dict.get ('ext', None)

            downloaded_audio_file = id + '.' + ext
            converted_audio_file = id + '.mp3'
            os.system ("ffmpeg -i " + downloaded_audio_file + " -b:a 24k " + converted_audio_file)
            os.unlink (id + '.' + ext)

            with open (converted_audio_file, 'rb') as f:
                await bot.sendDocument (chat_id, f, caption=title, reply_to_message_id=msg['message_id'])

            os.unlink (converted_audio_file)


if 2 != len (sys.argv):
    print ("Please provide Telegram bot token as an only argument")
    exit (1)

bot = telepot.aio.Bot (str (sys.argv[1]))
answerer = telepot.aio.helper.Answerer (bot)

loop = asyncio.get_event_loop ()
loop.create_task (MessageLoop (bot, {'chat': on_chat_message}).run_forever ())
print ('Listening ...')

loop.run_forever ()
