FROM python:3.9.6-slim-bullseye

LABEL version="0.1" \
    description="Telegram bot for adding a Fyysikkospeksi related frame to user's profile picture." \
    org.opencontainers.image.source="https://github.com/fyysikkokilta/fyysikkospeksi-taulubot"

COPY . /taulu
WORKDIR /taulu

RUN pip install -e . --no-cache-dir

ENTRYPOINT ["python", "taulubot/main.py"]