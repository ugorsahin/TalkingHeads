"""Copilot test"""

import os
import time
from pathlib import Path
import pytest

import generic
from utils import get_driver_arguments
from talkingheads import CopilotClient


def test_start():
    pytest.chathead = CopilotClient(**get_driver_arguments("copilot"))
    assert pytest.chathead.ready, "The Client is not ready"


def test_interaction():
    time.sleep(1)
    return generic.test_interaction()


def test_reset():
    ch = pytest.chathead
    _ = pytest.chathead.interact("How can I reset this thread?")
    assert ch.reset_thread(), "Reset operation has failed."
    perhaps_some_text = ch.get_last_response()
    assert perhaps_some_text != "", "Chat area is not empty."

def test_interaction_with_file():
    time.sleep(1)
    im_path = Path(os.path.dirname(__file__)) / "test_assets/one_cat.jpg"
    response = pytest.chathead.interact(
        "Without further ado, just write 'indeed' if there is a cat in the uploaded image",
        image_path=im_path,
    )
    assert (
        "indeed" in response.lower()
    ), f"The word indeed doesn't exist in the response, instead it responded {response}"


def test_delete_chathead():
    return generic.test_delete_chathead()
