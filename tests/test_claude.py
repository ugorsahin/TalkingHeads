"""Claude test"""

import time
import psutil
import pytest
from selenium.webdriver.common.by import By
from talkingheads import ClaudeClient
from utils import get_driver_arguments

def test_start():
    pytest.chathead = ClaudeClient(**get_driver_arguments("claude", incognito=False))
    assert pytest.chathead.ready, "The Client is not ready"

def test_interaction():
    time.sleep(1)
    answer = pytest.chathead.interact(
        "Without any explanation or extra information, just repeat the following: book."
    )
    answer_match = "book" in answer.lower()
    assert (
        answer_match
    ), f'Answer is not "book.", instead it returned {answer}'

def test_regenerate():
    first_answer = pytest.chathead.interact(
        "Without any explanation or extra information, type three animal names."
    ).lower()
    second_answer = pytest.chathead.regenerate_response()
    assert first_answer != second_answer, "The regenerated answer is the same."


def test_reset():
    assert pytest.chathead.reset_thread()
    time.sleep(1)
    resp = pytest.chathead.find_or_fail(
        By.XPATH, pytest.chathead.markers.chatarea_xq, return_type="last", fail_ok=True
    )
    assert (
        resp is None
    ), f"Chat is not empty {resp.text}"


def test_delete_chathead():
    del pytest.chathead
    assert not any(
        "undetected_chromedriver" in p.name() for p in psutil.process_iter()
    ), "Undetected chromedriver exists"
