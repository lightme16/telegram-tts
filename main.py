import os
import sys
from langdetect import detect

from pyrogram import Client, filters
from pyrogram.types import Message

from gtts import gTTS


def get_channel_name() -> None:
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        raise Exception("Please provide channel name")


CHANNEL_NAME = get_channel_name()

name = "tts-feed"
app = Client(name)


@app.on_message(filters.all)
def message_handler(client: Client, message: Message) -> None:
    if message.chat.title != CHANNEL_NAME:
        return
    print(message)
    from_user = " ".join(
        [n for n in [message.from_user.first_name, message.from_user.last_name] if n]
    )

    lang = "en"

    if message.forward_from_chat:
        txt = message.caption or message.text
        lang = detect(txt)
        from_user = f"forwared from {message.forward_from_chat.title}"
    elif message.media:
        txt = " ".join([n for n in [message.media, message.caption] if n])
        lang = detect(txt)
        if message.media == "voice":
            pass
    else:
        txt = message.text
        lang = detect(txt)

    print(f"from user: {from_user}, lang: {lang} text: {txt}")
    tts = gTTS(f"{from_user}: {txt}", lang=lang)

    file = f"{message.message_id}.mp3"

    tts.save(file)
    os.system(f"ffplay -autoexit -nodisp -af atempo=2 {file} && rm {file}")


app.run()
