# Fyysikkospeksi Taulubot

![Fyysikkospeksi logo](taulubot/images/speksilogo.png)

![example workflow](https://github.com/fyysikkokilta/fyysikkospeksi-taulubot/actions/workflows/ci.yaml/badge.svg)

Telegram bot for adding a [_Fyysikkospeksi_](https://fyysikkospeksi.fi/) related frame to user's profile picture.

Forked from [EinariTuukkanen/telegram-bots](https://github.com/EinariTuukkanen/telegram-bots).


## Deploying

### Docker (recommended)
1. Make a `.env`-file containing `TAULUBOT_TOKEN` and the corresponding token.
2. Run Docker with
    ```bash
    docker run -d --restart unless-stopped --env-file .env ghcr.io/fyysikkokilta/fyysikkospeksi-taulubot:main
    ```
    _Optionally_, to override the frame images, you can mount a folder with your images to `/taulu/taulubot/images`. 
    Mounting the current folder as read-only works as follows:
    ```bash
    docker run -d --volume ${pwd}:/taulu/taulubot/images:ro --env-file .env ghcr.io/fyysikkokilta/fyysikkospeksi-taulubot:main
    ```

### Python
1. Install dependencies w/
    ```bash
    pip install -e .
    ```
2. Set the `TAULUBOT_TOKEN` environment variable
    ```bash
    export TAULUBOT_TOKEN=1234:abcedf
    ```
3. Start the bot with `python taulubot/main.py`

Instead of 3. one can alternatively open a Python shell and run
   ```python
   from taulubot.main import main
   main()
   ```
   
## Development

1. Clone the repo
2. Install dependencies
    ```bash
    pip install -e .
    ```
    (optional) or the testing dependencies as well
    ```bash
    pip install -e .[test]
    ```
3. Start coding!


## Testing

Testing requires valid _TAULUBOT_TOKEN_TEST, TELEGRAM_APP_ID, TELEGRAM_APP_HASH,_ and _TELETHON_SESSION_ environment variables. 
Refer to [this guide on how to generate them](https://blog.1a23.com/2020/03/06/how-to-write-integration-tests-for-a-telegram-bot/).
After these are set up, tests can be run with:
```bash
pytest tests
```


## Frames

#### Normal
![Frame](taulubot/images/frame.png)

#### Rare
![Frame](taulubot/images/frame_rare.png)

#### Mythic rare
![Frame](taulubot/images/frame_mythicrare.png)
