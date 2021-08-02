FROM python:3.9.6-alpine

LABEL version="0.1" \
    description="Telegram bot for adding a Fyysikkospeksi related frame to user's profile picture." \
    org.opencontainers.image.source="https://github.com/fyysikkokilta/fyysikkospeksi-taulubot"

COPY . /taulu
WORKDIR /taulu

# Install deps. for Pillow on alpine
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk add jpeg-dev zlib-dev libjpeg \
    && pip install Pillow \
    && apk del build-deps
RUN pip install -e . --no-cache-dir

ENTRYPOINT ["python", "taulubot/main.py"]