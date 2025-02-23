import pytest
import psutil
import random

async def test_interaction(chathead):
    num1 = random.randint(0, 20)
    num2 = random.randint(0, 20)
    answer = str(num1 + num2)

    response = await chathead.interact(
        f"Without further explanation, provide the numerical answer of the following question: {num1} + {num2}"
    )
    assert (
        answer in response.lower()
    ), f'response is not "{answer}", the full response: {response}'

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
