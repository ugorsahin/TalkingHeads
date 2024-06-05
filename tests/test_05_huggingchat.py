"""HuggingChat test"""

import time
import psutil
import pytest
from selenium.webdriver.common.by import By
from talkingheads import HuggingChatClient
from utils import get_driver_arguments

def test_start():
    pytest.chathead = HuggingChatClient(**get_driver_arguments('huggingchat', incognito=True))
    assert pytest.chathead.ready, "The Client is not ready"


def test_model_selection():
    assert pytest.chathead.switch_model(
        "google/gemma-1.1-7b-it"
    ), "Model switch failed."
    assert not pytest.chathead.switch_model(
        "dream-company/dream-model"
    ), "Unexpected model switch."


def test_interaction():
    time.sleep(1)
    response = pytest.chathead.interact(
        "Without any explanation or extra information, just repeat the following: book."
    )
    assert (
        "book" in response.lower()
    ), f'response is not "book.", instead it returned {response}'


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

# Searching web is unstable, huggingchat fails to search web sometimes.
# def test_search_web():
#     pytest.chathead.toggle_search_web()
#     response = pytest.chathead.interact(
#         "Search the following keywords: Teaterkriget  site:wikipedia.org.\n" \
#         "After you searched, based on your results," \
#         "write the starting and ending date in DD/MM/YYYY format"
#     )
#     assert (
#         "24/09/1788" in response.lower() and "09/07/1789" in response.lower()
#     ), f'The dates are not in correct format or the result doesn\'t have the dates: {response}'

def test_delete_chathead():
    del pytest.chathead
    assert not any(
        "undetected_chromedriver" in p.name() for p in psutil.process_iter()
    ), "Undetected chromedriver exists"
