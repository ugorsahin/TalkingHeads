"""Copilot test"""

import asyncio
import pytest

import generic
from utils import get_driver_arguments
from talkingheads import DeepSeekClient

@pytest.mark.asyncio(loop_scope='session')
async def test_start():
    pytest.chathead = DeepSeekClient(**get_driver_arguments("deepseek"), skip_login=True)
    await pytest.chathead.start()
    assert pytest.chathead.ready, "The Client is not ready"

@pytest.mark.asyncio(loop_scope='session')
async def test_interaction():
    await asyncio.sleep(1)
    await generic.test_interaction(pytest.chathead)

@pytest.mark.asyncio(loop_scope='session')
async def test_reset():
    await generic.test_reset(pytest.chathead)


@pytest.mark.asyncio(loop_scope='session')
async def test_delete_chathead():
    await generic.test_delete_chathead(pytest.chathead)
