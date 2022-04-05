import asyncio
import configparser
import functools
import json
import os
import re
from typing import Optional, Tuple, TypedDict

from gtts import gTTS
from langdetect import detect_langs
from langdetect.language import Language
from pyrogram import Client, filters
from pyrogram.types import Message

LANGS_PRIORITY = ["en", "ru", "uk", "mk"]

OptionsType = TypedDict('OptionsType', {'enabled': bool, 'alias': str, 'send_audio': bool})


def parse_config_ini():
    config_ini = os.path.join(os.path.dirname(__file__), "config.ini")
    if not os.path.exists(config_ini):
        raise Exception(f"config.ini not found in {config_ini}")
    config = configparser.ConfigParser()
    config.read(config_ini)
    return config


def get_channels() -> dict[str, OptionsType]:
    config = parse_config_ini()
    channels: dict[str, OptionsType] = {}
    for channel, options in config.items("channels"):
        channels[channel] = json.loads(options)
    return channels


channels = get_channels()

app = Client("tts-feed")


def remove_unicode(txt: str) -> str:
    return txt.encode("ascii", "ignore").decode("ascii")


@app.on_message(filters.all)
async def message_handler(client: Client, message: Message) -> None:
    chat_title = message.chat.title and message.chat.title.lower()
    user = message.chat.username and message.chat.username.lower()
    if chat_title not in channels and user not in channels:
        return
    options: Optional[OptionsType] = channels.get(chat_title, {})
    if options is not None and options.get("enabled") is not False:
        await process_text(client, message, options)


async def play_audio(file: str) -> None:
    await run_cmd(
        f"ffmpeg -loglevel error -i {file} -filter:a 'atempo=2' -f matroska - | ffplay -autoexit -nodisp -loglevel error - ")


async def run_cmd(cmd: str) -> None:
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


async def process_text(client: Client, message: Message, options: OptionsType):
    sender, lang, txt = parse(message, options)
    file = generate_audiofile(sender, lang, message.message_id, txt)
    tasks = [
        play_audio(file),
    ]
    if options.get("send_audio") is True:
        tasks.append(client.send_audio(message.chat.id, audio=file, reply_to_message_id=message.message_id))
    await asyncio.gather(*tasks)
    await run_cmd(f"rm {file}")


def parse(message: Message, options: OptionsType) -> Tuple[str, str, str]:
    chat_title = options.get("alias", deEmojify(message.chat.title))
    if message.from_user:
        sender = " ".join(
            [
                n
                for n in [message.from_user.first_name, message.from_user.last_name]
                if n
            ]
        )
    else:
        sender = "Unknown"

    if message.forward_from_chat:
        txt = message.caption or message.text
        lang = detect_lang(txt)
        sender = f"forwared from {message.forward_from_chat.title}"
    elif message.media:
        txt = " ".join([n for n in [message.media, message.caption] if n])
        lang = detect_lang(txt)
        if message.media == "voice":
            pass
    else:
        txt = message.text
        lang = detect_lang(txt)

    txt = f"{chat_title}      {txt}"
    sender = deEmojify(sender)
    return sender, lang, txt


def deEmojify(text: str) -> str:
    regrex_pattern = re.compile(
        pattern="["
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F680-\U0001F6FF"  # transport & map symbols
                "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "]+",
        flags=re.UNICODE,
    )
    return regrex_pattern.sub(r"", str(text)).strip()


def detect_lang(txt: str) -> str:
    lang = LANGS_PRIORITY[0]
    try:
        langs: list[Language] = detect_langs(txt)
    except:
        return lang

    print(f"detected langs: {langs}")
    langs = [l for l in langs if l.lang in LANGS_PRIORITY]
    if langs:
        lang = langs[0].lang
    # FIXME: workaround against match errors
    if lang == "mk":
        lang = "ru"
    return lang


# deal with duplicates
@functools.lru_cache(maxsize=256)
def generate_audiofile(sender: str, lang: str, message_id: int, txt: str) -> str:
    print(f"sender: {sender}, lang: {lang} text: {txt}")
    tts = gTTS(f"{sender}: {txt}", lang=lang)
    file1 = f"{message_id}.ogg"
    tts.save(file1)
    return file1


app.run()
