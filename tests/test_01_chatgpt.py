"""ChatGPT test"""

import asyncio
import pytest
import generic
from utils import get_driver_arguments
from talkingheads.model_library import ChatGPTClient


@pytest.mark.asyncio(loop_scope='session')
async def test_start():
    pytest.chathead = ChatGPTClient(**get_driver_arguments('chatgpt'))
    await pytest.chathead.start()
    assert pytest.chathead.ready, "The Client is not ready"

@pytest.mark.asyncio(loop_scope='session')
async def test_interaction():
    await asyncio.sleep(2)
    await generic.test_interaction(pytest.chathead)

@pytest.mark.asyncio(loop_scope='session')
async def test_reset():
    await asyncio.sleep(2)
    await generic.test_reset(pytest.chathead)

@pytest.mark.asyncio(loop_scope='session')
async def test_regenerate():
    await asyncio.sleep(2)
    first_response = await pytest.chathead.interact(
        "Without any explanation or extra information, type three animal names."
    )
    second_response = await pytest.chathead.regenerate_response()
    assert first_response.lower() != second_response.lower(), "The regenerated response is the same."

@pytest.mark.asyncio(loop_scope='session')
async def test_custom_interactions():
    mod_text = "Lorem ipsum dolor sit amet"
    info_text = "consectetur adipiscing elit"
    await pytest.chathead.set_custom_instruction("modulation", mod_text)
    await asyncio.sleep(1)
    applied_mod_text = await pytest.chathead.get_custom_instruction("modulation")
    assert (
        applied_mod_text == mod_text
    ), f"Modulation text is different: {applied_mod_text}"
    await pytest.chathead.set_custom_instruction("extra_information", info_text)
    await asyncio.sleep(1)
    applied_extra_text = await pytest.chathead.get_custom_instruction("extra_information")
    assert (
        applied_extra_text == info_text
    ), f"Info text is different {applied_extra_text}"

@pytest.mark.asyncio(loop_scope='session')
async def test_delete_chathead():
    await generic.test_delete_chathead(pytest.chathead)
