import os
import sys
from langdetect import detect, detect_langs
from langdetect.language import Language

from pyrogram import Client, filters
from pyrogram.types import Message

from gtts import gTTS

LANGS_PRIORITY = ["en", "ru", "uk"]


def get_channel_name() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        raise Exception("Please provide channel name")


CHANNEL_NAME = get_channel_name()

app = Client("tts-feed")


@app.on_message(filters.all)
def message_handler(client: Client, message: Message) -> None:
    if message.chat.title != CHANNEL_NAME:
        return
    from_user, lang, txt = parse(message)
    play(from_user, lang, message, txt)


def parse(message: Message) -> (str, str, str):
    from_user = " ".join(
        [n for n in [message.from_user.first_name, message.from_user.last_name] if n]
    )
    if message.forward_from_chat:
        txt = message.caption or message.text
        lang = detect_lang(txt)
        from_user = f"forwared from {message.forward_from_chat.title}"
    elif message.media:
        txt = " ".join([n for n in [message.media, message.caption] if n])
        lang = detect_lang(txt)
        if message.media == "voice":
            pass
    else:
        txt = message.text
        lang = detect_lang(txt)

    return from_user, lang, txt


def detect_lang(txt):
    langs: list[Language] = detect_langs(txt)
    print(f"detected langs: {langs}")
    langs = [l for l in langs if l.lang in LANGS_PRIORITY]
    if langs:
        lang = langs[0].lang
    else:
        lang = LANGS_PRIORITY[0]
    return lang


def play(from_user: str, lang: str, message: Message, txt: str) -> None:
    print(f"from user: {from_user}, lang: {lang} text: {txt}")
    tts = gTTS(f"{from_user}: {txt}", lang=lang)
    file = f"{message.message_id}.mp3"
    tts.save(file)
    os.system(
        f"ffplay -autoexit -nodisp -af atempo=2 -loglevel error {file} && rm {file}"
    )


app.run()
