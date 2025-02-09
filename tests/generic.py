import pytest
import psutil

async def test_interaction(chathead):
    response = await chathead.interact(
        "What object is most often found on a bookshelf?"
    )
    assert (
        "book" in response.lower()
    ), f'response is not "book.", the full response: {response}'

async def test_delete_chathead(chathead):
    chathead.browser.stop()
    del chathead
    assert not any(
        "nodriver" in p.name() for p in psutil.process_iter()
    ), "nodriver exists"

async def test_reset(chathead):
    assert await chathead.reset_thread()
    chat_item = await chathead.find_or_fail(chathead.markers.chatbox, fail_ok=True)
    assert (
        chat_item is None
    ), "Chat is not empty"
