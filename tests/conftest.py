import asyncio
import os
import subprocess

import pytest
from telethon import TelegramClient
from telethon.sessions import StringSession

api_id = int(os.environ["TELEGRAM_APP_ID"])
api_hash = os.environ["TELEGRAM_APP_HASH"]
session_str = os.environ["TELETHON_SESSION"]


@pytest.fixture(scope="session", autouse=True)
def server():
    """ Start the Bot before testing """
    process = subprocess.Popen(['python', '-c', "from taulubot.main import main;main()"])  # , shell=True, check=True)
    yield process
    # executed after last test
    process.kill()


@pytest.fixture(scope="session")
async def client() -> TelegramClient:
    """Set up Telegram Client to interact w/ bot"""
    tg_client = TelegramClient(
        StringSession(session_str), api_id, api_hash,
        sequential_updates=True
    )
    # Connect to the server
    await tg_client.connect()
    await tg_client.get_me()
    await tg_client.get_dialogs()

    yield tg_client

    await tg_client.disconnect()
    await tg_client.disconnected


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for all test cases."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
