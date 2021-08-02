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
    docker run -d --env-file .env fyysikkokilta/fyysikkospeksi-taulubot
    ```

_Optionally_, to override the frame images, you can mount a folder with your images to `/taulu/taulubot/images`. 
Mounting the current folder as read-only works as follows:
```bash
docker run -d --volume ${pwd}:/taulu/taulubot/images:ro --env-file .env fyysikkokilta/fyysikkospeksi-taulubot
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

## Frames

![Frame](taulubot/images/frame.png)
![Frame](taulubot/images/frame_rare.png)
![Frame](taulubot/images/frame_mythicrare.png)
