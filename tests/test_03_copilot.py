"""Copilot test"""

import os
import time
from pathlib import Path
import psutil
import pytest
from talkingheads import CopilotClient
from utils import get_driver_arguments


def test_start():
    pytest.chathead = CopilotClient(**get_driver_arguments("copilot"))
    assert pytest.chathead.ready, "The Client is not ready"


def test_model():
    model_type = pytest.chathead.get_models(get_active_model=True)
    assert model_type == "Balanced", "Model is not balanced"

    assert pytest.chathead.switch_model("Creative"), "Unable to switch to Creative"
    model_type = pytest.chathead.get_models(get_active_model=True)
    assert model_type == "Creative", "Model is not Creative"

    assert pytest.chathead.switch_model("Balanced"), "Unable to switch to Balanced"
    model_type = pytest.chathead.get_models(get_active_model=True)
    assert model_type == "Balanced", "Model is not Balanced"

    assert not pytest.chathead.switch_model("dream-model"), "Unexpected model switch"


def test_plugins():
    ch = pytest.chathead
    assert ch.toggle_plugin("Kayak"), "Couldn't enable Kayak plugin"
    assert ch.get_plugin("Kayak").is_selected(), "Kayak plugin is not enabled"
    assert ch.toggle_plugin("Kayak"), "Couldn't enable Kayak plugin"
    assert ch.get_plugin("Kayak"), "Kayak plugin is not disabled"
    assert not ch.get_plugin("dream-plugin"), "Unexpected plugin switch"


def test_interaction():
    time.sleep(1)
    response = pytest.chathead.interact(
        "Without any explanation or extra information, just repeat the following: book."
    )
    assert (
        "book" in response.lower()
    ), f'response is not "book.", instead it returned {response}'


def test_reset():
    ch = pytest.chathead
    response = pytest.chathead.interact(
        "Without any explanation or extra information, just repeat the following: student."
    )
    assert ch.reset_thread(), "Reset operation has failed."
    greeting_text = ch.get_last_response(check_greeting=True)
    assert greeting_text != response, "The last response is still the same."


def test_interaction_with_file():
    im_path = Path(os.path.dirname(__file__)) / "test_assets/one_cat.jpg"
    response = pytest.chathead.interact(
        "Without further ado, just write 'indeed' if there is a cat in the uploaded image",
        image_path=im_path,
    )
    assert (
        "indeed" in response.lower()
    ), f"The word indeed doesn't exist in the response, instead it responded {response}"


def test_delete_chathead():
    del pytest.chathead
    assert not any(
        "undetected_chromedriver" in p.name() for p in psutil.process_iter()
    ), "Undetected chromedriver exists"
