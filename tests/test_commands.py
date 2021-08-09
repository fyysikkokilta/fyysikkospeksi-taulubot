import pytest
from telethon import TelegramClient
from telethon.tl.custom.message import Message


@pytest.mark.asyncio
async def test_help(client: TelegramClient):
    # Test the /help command
    async with client.conversation("fyysikkospeksi_taulubot", timeout=10) as conv:
        # Send a command
        await conv.send_message("/help")
        # Get response
        resp: Message = await conv.get_response()
        # Make assertions
        assert "/taulu" in resp.text


@pytest.mark.skip(reason="Fetching a photo from TG test server is harder than changing base_url")
@pytest.mark.asyncio
async def test_taulu(client: TelegramClient):
    # Test the /taulu command
    async with client.conversation("fyysikkospeksi_taulubot", timeout=15) as conv:
        # Test w/ profile picture
        # await client(UploadProfilePhotoRequest(
        #     await client.upload_file('./taulubot/images/frame.png')
        # ))

        await conv.send_message("/taulu")
        resp: Message = await conv.get_response()

        assert resp.photo
