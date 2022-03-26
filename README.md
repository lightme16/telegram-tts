# telegram-tts

The script that listens for updates for gives telegram chats or channels and plays incoming messages using TTS engine.

## How to use

1. Get telegram api token, insert it into `config.ini`.
2. Provide channels to subscribe in config (See Config section below).
3. Install `pipenv` with `pip install pipenv`.
4. Install pipenv requirements `pipenv sync`
5. Install `ffmpeg` that used to play messages.
6. Run script with `pipenv run python main.py.

## Config

Provide your config in `config.ini`

```
[pyrogram]
api_id = YOUR_API_ID
api_hash = YOUR_API_HASH

[channels]
Durov's Channel = {"alias": "durov", "enabled": true}
mrAnderson = {"enabled": true}
```
