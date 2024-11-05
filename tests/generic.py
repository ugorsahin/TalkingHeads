import pytest
import time
import psutil

def test_interaction():
    response = pytest.chathead.interact(
        "What object is most often found on a bookshelf?"
    )
    assert (
        "book" in response.lower()
    ), f'response is not "book.", the full response: {response}'
    time.sleep(0.5)

def test_delete_chathead():
    del pytest.chathead
    assert not any(
        "undetected_chromedriver" in p.name() for p in psutil.process_iter()
    ), "Undetected chromedriver exists"
