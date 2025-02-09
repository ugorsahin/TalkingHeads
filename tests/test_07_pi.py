"""Pi test"""

import asyncio
import pytest

import generic
from utils import get_driver_arguments
from talkingheads import PiClient


@pytest.mark.asyncio(loop_scope='session')
async def test_start():
    pytest.chathead = PiClient(**get_driver_arguments("pi", incognito=True))
    await pytest.chathead.start()
    assert pytest.chathead.ready, "The Client is not ready"


@pytest.mark.asyncio(loop_scope='session')
async def test_interaction():
    await asyncio.sleep(1)
    await generic.test_interaction(pytest.chathead)


@pytest.mark.asyncio(loop_scope='session')
async def test_reset():
    assert await pytest.chathead.reset_thread()
    chat_item = await pytest.chathead.find_or_fail(pytest.chathead.markers.chatbox, fail_ok=True, return_type='all')
    assert (
        len(chat_item) == 1
    ), "Chat is not empty"


@pytest.mark.asyncio(loop_scope='session')
async def test_delete_chathead():
    await generic.test_delete_chathead(pytest.chathead)
