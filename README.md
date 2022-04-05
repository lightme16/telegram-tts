# telegram-tts

The script listens for updates for gives telegram DM chats or channels and generated audio for the messages.

## Features
- To read message out loud is `read_aloud` flag is set to true. Useful when script is running at the desktop and you want to have radio-like experience for popular channel.
- To reply with the audio version of the text message is `send_audio` flag is set to true. Useful when you want to occasionally generate audio for particular message e.g big news articles and listen with our telegram client. You could run this scrip on the remote serverless for this mode.

## How to use

1. Get telegram api token, insert it into `config.ini`.
2. Provide channels to subscribe in config (See Config section below).
3. Install `pipenv` with `pip install pipenv`.
4. Install pipenv requirements `pipenv sync`
5. Install `ffmpeg` that used to play messages.
6. Run script with `pipenv run python main.py.

Please, note that this is not a telegram bot. It is a simple script that uses real user account and communicates telegram API to get updates and generate audio for the messages.    


## Config

Provide your config in `config.ini`

```
[pyrogram]
api_id = YOUR_API_ID
api_hash = YOUR_API_HASH

[channels]
Durov's Channel = {"alias": "durov", "read_aloud": true}
mrAnderson = {"read_aloud": true, "send_audio": true}
```
