"""Copilot test"""

import time
import psutil
import pytest
from talkingheads import CopilotClient
from utils import get_driver_arguments

def test_start():
    pytest.chathead = CopilotClient(**get_driver_arguments('copilot', incognito=False))
    assert pytest.chathead.ready, "The Client is not ready"


def test_interaction():
    time.sleep(1)
    answer = pytest.chathead.interact(
        "Without any explanation or extra information, just repeat the following: book."
    )
    assert (
        "book" in answer.lower()
    ), f'Answer is not "book.", instead it returned {answer}'

def test_reset():
    ch = pytest.chathead
    answer = pytest.chathead.interact(
        "Without any explanation or extra information, just repeat the following: student."
    )
    assert ch.reset_thread(), "Reset operation has failed."
    greeting_text = ch.get_last_answer(check_greeting=True)
    assert greeting_text != answer, "The last response is still the same."


def test_model():
    assert (
        pytest.chathead.get_models(get_active_model=True) == "Balanced"
    ), "Model is not balanced"
    assert pytest.chathead.switch_model("Creative"), "Unable to switch to Creative"
    assert (
        pytest.chathead.get_models(get_active_model=True) == "Creative"
    ), "Model is not Creative"
    assert pytest.chathead.switch_model("Balanced"), "Unable to switch to Balanced"
    assert (
        pytest.chathead.get_models(get_active_model=True) == "Balanced"
    ), "Model is not Balanced"


def test_plugins():
    ch = pytest.chathead
    assert ch.toggle_plugin("Kayak"), "Couldn't enable Kayak plugin"
    time.sleep(1)
    assert ch.get_plugin("Kayak").is_selected(), "Kayak plugin is not enabled"
    time.sleep(1)
    assert ch.toggle_plugin("Kayak"), "Couldn't enable Kayak plugin"
    time.sleep(1)
    assert ch.get_plugin("Kayak"), "Kayak plugin is not disabled"


def test_delete_chathead():
    del pytest.chathead
    assert not any(
        "undetected_chromedriver" in p.name() for p in psutil.process_iter()
    ), "Undetected chromedriver exists"
