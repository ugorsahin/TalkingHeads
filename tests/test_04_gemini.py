"""Gemini test"""

# import time
import os
from pathlib import Path
import psutil
import pytest
from selenium.webdriver.common.by import By
import talkingheads
from utils import get_driver_arguments

def test_start():
    pytest.chathead = talkingheads.GeminiClient(**get_driver_arguments("gemini"))
    assert pytest.chathead.ready, "The Client is not ready"


def test_interaction():
    response = pytest.chathead.interact(
        "Without any explanation or extra information, just repeat the following: book."
    )
    assert (
        "book" in response.lower()
    ), f'response is not "book.", instead it responded {response}'


def test_regenerate():
    first_response = pytest.chathead.interact(
        "Without any explanation or extra information, type three animal names."
    ).lower()
    second_response = pytest.chathead.regenerate_response()
    assert first_response != second_response, "The regenerated response is the same."


def test_interaction_with_file():
    im_path = Path(os.path.dirname(__file__)) / 'test_assets/one_cat.jpg'
    response = pytest.chathead.interact(
        "Without further ado, just write 'indeed' if there is a cat in the uploaded image",
        image_path=im_path
    )
    assert (
        "indeed" in response.lower()
    ), f"The word indeed doesn't exist in the response, instead it responded {response}"

def test_model():
    assert not pytest.chathead.switch_model("dream-model"), "Unexpected switch model behaviour"


def test_modify_response():
    response = pytest.chathead.interact(
        "What is a real number?"
    )
    new_response = pytest.chathead.modify_response("shorter")
    assert len(response) > len(new_response), "The new response longer!"


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


def test_delete_chathead():
    del pytest.chathead
    assert not any(
        "undetected_chromedriver" in p.name() for p in psutil.process_iter()
    ), "Undetected chromedriver exists"
