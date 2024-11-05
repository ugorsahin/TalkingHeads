"""Gemini test"""

# import time
import os
import time
from pathlib import Path
import pytest
from selenium.webdriver.common.by import By

import generic
from utils import get_driver_arguments
from talkingheads import GeminiClient

def test_start():
    pytest.chathead = GeminiClient(**get_driver_arguments("gemini"))
    assert pytest.chathead.ready, "The Client is not ready"


def test_interaction():
    return generic.test_interaction()


def test_model():
    assert not pytest.chathead.switch_model("dream-model"), "Unexpected switch model behaviour"
    time.sleep(0.5)


def test_modify_response():
    response = pytest.chathead.interact(
        "What is a real number?"
    )
    new_response = pytest.chathead.modify_response("shorter")
    assert len(response) > len(new_response), "The new response longer!"
    time.sleep(0.5)


def test_reset():
    assert pytest.chathead.reset_thread()
    assert (
        len(
            pytest.chathead.browser.find_elements(
                By.TAG_NAME, pytest.chathead.markers.chatbox_tq
            )
        )
        == 0
    ), "Chat is not empty"
    time.sleep(0.5)

def test_interaction_with_file():
    im_path = Path(os.path.dirname(__file__)) / 'test_assets/one_cat.jpg'
    response = pytest.chathead.interact(
        "Without further ado, just write 'indeed' if there is a cat in the uploaded image",
        image_path=im_path
    )
    assert (
        "indeed" in response.lower()
    ), f"The word indeed doesn't exist in the response, instead it responded {response}"
    time.sleep(0.5)

def test_delete_chathead():
    return generic.test_delete_chathead()
