import configparser
import os

from gtts import gTTS
from langdetect import detect_langs
from langdetect.language import Language
from pyrogram import Client, filters
from pyrogram.types import Message

LANGS_PRIORITY = ["en", "ru", "uk"]


def parse_config_ini():
    config_ini = os.path.join(os.path.dirname(__file__), "config.ini")
    if not os.path.exists(config_ini):
        raise Exception(f"config.ini not found in {config_ini}")
    config = configparser.ConfigParser()
    config.read(config_ini)
    return config


def get_channels() -> list[str]:
    config = parse_config_ini()
    return config.get("channels", "names")


channels = get_channels()
print(f"Channels: {channels}")


app = Client("tts-feed")


@app.on_message(filters.all)
def message_handler(client: Client, message: Message) -> None:
    chat_title = message.chat.title
    if chat_title not in channels:
        return
    from_user, lang, txt = parse(message)
    play(from_user, lang, message, txt)


def parse(message: Message) -> (str, str, str):
    chat_title = message.chat.title
    if message.from_user:
        from_user = " ".join(
            [n for n in [message.from_user.first_name, message.from_user.last_name] if n]
        )
    else:
        from_user = "Unknown"

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

    txt = f"{chat_title}      {txt}"
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
