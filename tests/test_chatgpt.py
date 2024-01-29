"""ChatGPT test"""

import pytest
from selenium.webdriver.common.by import By
from talkingheads import ChatGPTClient


def test_start():
    pytest.chathead = ChatGPTClient(headless=True, verbose=True)
    assert pytest.chathead.ready, "The Client is not ready"


def test_interaction():
    answer = pytest.chathead.interact(
        "Without any explanation or extra information, just repeat the following: book."
    )
    assert (
        "book" in answer.lower()
    ), f'Answer is not "book.", instead it returned {answer}'


def test_reset():
    assert pytest.chathead.reset_thread()
    assert (
        len(
            pytest.chathead.browser.find_elements(
                By.XPATH, pytest.chathead.markers.chatbox_xq
            )
        )
        == 0
    ), "Chat is not empty"


def test_regenerate():
    first_answer = pytest.chathead.interact(
        "Without any explanation or extra information, type three animal names."
    ).lower()
    second_answer = pytest.chathead.regenerate_response()
    assert first_answer != second_answer, "The regenerated answer is the same."


def test_custom_interactions():
    mod_text = "Lorem ipsum dolor sit amet"
    info_text = "consectetur adipiscing elit"
    pytest.chathead.set_custom_instruction("modulation", mod_text)
    applied_mod_text = pytest.chathead.get_custom_instruction("modulation")
    assert (
        applied_mod_text == mod_text
    ), f"Modulation text is different: {applied_mod_text}"
    pytest.chathead.set_custom_instruction("extra_information", info_text)
    applied_extra_text = pytest.chathead.get_custom_instruction("extra_information")
    assert (
        applied_extra_text == info_text
    ), f"Info text is different {applied_extra_text}"


def pytest_sessionfinish(session, exitstatus):
    del pytest.chathead
