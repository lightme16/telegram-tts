import asyncio
import os
import sys
from langdetect import detect

from pyrogram import Client, filters
from pyrogram.types import Dialog, Message

from gtts import gTTS


def get_channel_name() -> None:
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        raise Exception("Please provide channel name")


CHANNEL_NAME = get_channel_name()

name = "tts-feed"
app = Client(name)


async def find_chat(app: Client) -> Dialog:
    async for d in app.iter_dialogs():
        if d.chat.title == CHANNEL_NAME:
            print(f"Chat id is {d.chat.id}")
            return d


async def main() -> None:
    await app.start()

    @app.on_message(filters.all)
    def message_handler(client: Client, message: Message) -> None:
        if message.chat.title != CHANNEL_NAME:
            return
        print(message)
        from_user = " ".join(
            [
                n
                for n in [message.from_user.first_name, message.from_user.last_name]
                if n
            ]
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

        print(f"from user: {from_user}, lang: {lang}")
        tts = gTTS(f"{from_user}: {txt}", lang=lang)

        file = f"{message.message_id}.mp3"

        tts.save(file)
        print("playing")
        os.system(f"ffplay -autoexit -nodisp -af atempo=2 {file} && rm {file}")
        print("done")

    my_chat = await find_chat(app)
    if not my_chat:
        raise Exception("Cannot find target chat")
    while True:
        print("Sending claim message")
        print("Sleeping for a day...")
        await asyncio.sleep(60 * 60 * 24)


app.run(main())
