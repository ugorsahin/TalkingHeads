"""Pi test"""

import time
import pytest

import generic
from utils import get_driver_arguments
from talkingheads import PiClient


def test_start():
    pytest.chathead = PiClient(**get_driver_arguments("pi", incognito=True))
    assert pytest.chathead.ready, "The Client is not ready"


def test_interaction():
    time.sleep(1)
    generic.test_interaction()


def test_reset():
    assert pytest.chathead.reset_thread(), "Failed to reset"


def test_delete_chathead():
    return generic.test_delete_chathead()
