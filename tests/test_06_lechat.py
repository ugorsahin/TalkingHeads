"""LeChat test"""

import time
import pytest
from selenium.webdriver.common.by import By

import generic
from utils import get_driver_arguments
from talkingheads import LeChatClient

def test_start():
    pytest.chathead = LeChatClient(
        **get_driver_arguments("lechat", incognito=True)
    )
    assert pytest.chathead.ready, "The Client is not ready"


def test_interaction():
    time.sleep(1)
    generic.test_interaction()


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
    assert pytest.chathead.switch_model("Codestral"), "Model switch failed."
    assert not pytest.chathead.switch_model("dream-model"), "Unexpected model switch"


def test_delete_chathead():
    generic.test_delete_chathead()
