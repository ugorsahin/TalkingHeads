"""LeChat test"""

import asyncio
import pytest

import generic
from utils import get_driver_arguments
from talkingheads import LeChatClient


@pytest.mark.asyncio(loop_scope="session")
async def test_start():
    pytest.chathead = LeChatClient(**get_driver_arguments("lechat"), skip_login=True)
    await pytest.chathead.start()
    assert pytest.chathead.ready, "The Client is not ready"


@pytest.mark.asyncio(loop_scope="session")
async def test_interaction():
    await asyncio.sleep(1)
    await generic.test_interaction(pytest.chathead)


@pytest.mark.asyncio(loop_scope="session")
async def test_reset():
    assert await generic.test_reset(pytest.chathead)
    assert item is None, "Chat is not empty"


@pytest.mark.asyncio(loop_scope="session")
async def test_regenerate():
    first_response = await pytest.chathead.interact(
        "Without any explanation or extra information, type five animal names."
    )
    second_response = await pytest.chathead.regenerate_response()
    assert (
        first_response.lower() != second_response.lower()
    ), "The regenerated response is the same."


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_chathead():
    await generic.test_delete_chathead(pytest.chathead)
