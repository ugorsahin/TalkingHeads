"""LeChat test"""

import time
import psutil
import pytest
from selenium.webdriver.common.by import By
from talkingheads import LeChatClient
from utils import get_driver_arguments


def test_start():
    pytest.chathead = LeChatClient(
        **get_driver_arguments("lechat", incognito=True)
    )
    assert pytest.chathead.ready, "The Client is not ready"


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


def test_regenerate():
    first_response = pytest.chathead.interact(
        "Without any explanation or extra information, type three animal names."
    ).lower()
    second_response = pytest.chathead.regenerate_response()
    assert first_response != second_response, "The regenerated response is the same."


def test_model_selection():
    assert pytest.chathead.switch_model("Next"), "Model switch failed."
    assert not pytest.chathead.switch_model("dream-model"), "Unexpected model switch"


def test_delete_chathead():
    del pytest.chathead
    assert not any(
        "undetected_chromedriver" in p.name() for p in psutil.process_iter()
    ), "Undetected chromedriver exists"
