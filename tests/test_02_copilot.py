"""Copilot test"""

import asyncio
import os
from pathlib import Path
import pytest

import generic
from utils import get_driver_arguments
from talkingheads import CopilotClient

@pytest.mark.asyncio(loop_scope='session')
async def test_start():
    pytest.chathead = CopilotClient(**get_driver_arguments("copilot"))
    await pytest.chathead.start()
    assert pytest.chathead.ready, "The Client is not ready"

@pytest.mark.asyncio(loop_scope='session')
async def test_interaction():
    await generic.test_interaction(pytest.chathead)
    await asyncio.sleep(1)

@pytest.mark.asyncio(loop_scope='session')
async def test_reset():
    await generic.test_reset(pytest.chathead)

@pytest.mark.asyncio(loop_scope='session')
async def test_interaction_with_file():
    await asyncio.sleep(1)
    im_path = Path(os.path.dirname(__file__)) / "test_assets/one_cat.jpg"
    response = await pytest.chathead.interact(
        "Without further ado, just write 'indeed' if there is a cat in the uploaded image",
        image_path=im_path,
    )
    assert (
        "indeed" in response.lower()
    ), f"The word indeed doesn't exist in the response, instead it responded {response}"

@pytest.mark.asyncio(loop_scope='session')
async def test_delete_chathead():
    await generic.test_delete_chathead(pytest.chathead)
