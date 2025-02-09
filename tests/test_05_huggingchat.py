"""HuggingChat test"""

import asyncio
import pytest

import generic
from utils import get_driver_arguments
from talkingheads import HuggingChatClient

@pytest.mark.asyncio(loop_scope='session')
async def test_start():
    pytest.chathead = HuggingChatClient(**get_driver_arguments('huggingchat', incognito=True))
    await pytest.chathead.start()
    assert pytest.chathead.ready, "The Client is not ready"


@pytest.mark.asyncio(loop_scope='session')
async def test_model_selection():
    assert await pytest.chathead.switch_model(
        "microsoft/Phi-3.5-mini-instruct"
    ), "Model switch failed."
    assert not await pytest.chathead.switch_model(
        "dream-company/dream-model"
    ), "Unexpected model switch."

@pytest.mark.asyncio(loop_scope='session')
async def test_interaction():
    await asyncio.sleep(1)
    await generic.test_interaction(pytest.chathead)


@pytest.mark.asyncio(loop_scope='session')
async def test_reset():
    await generic.test_reset(pytest.chathead)

# Searching web is unstable, huggingchat fails to search web sometimes.
# @pytest.mark.asyncio(loop_scope='session')
# async def test_search_web():
#     await pytest.chathead.toggle_search_web()
#     response = await pytest.chathead.interact(
#         "Search the following keywords: Teaterkriget  site:wikipedia.org.\n" \
#         "After you searched, based on your results," \
#         "write the starting and ending date in DD/MM/YYYY format"
#     )

#     assert (
#         "24/09/1788" in response.lower() and "09/07/1789" in response.lower()
#     ), f'The dates are not in correct format or the result doesn\'t have the dates: {response}'

@pytest.mark.asyncio(loop_scope='session')
async def test_delete_chathead():
    await generic.test_delete_chathead(pytest.chathead)
