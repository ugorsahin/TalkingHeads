'''HuggingChat test'''

import time
import pytest
from talkingheads import PiClient

def test_start():
    pytest.chathead = PiClient(
        headless=True,
        verbose=True
    )
    assert pytest.chathead.ready, 'The Client is not ready'

def test_interaction():
    time.sleep(1)
    answer = pytest.chathead.interact(
        'Without any explanation or extra information, just repeat the following: book.')
    assert 'book' in answer.lower(), f'Answer is not "book.", instead it returned {answer}'

def test_model_selection():
    assert pytest.chathead.switch_model('SupportPi'), 'Model switch failed.'

def pytest_sessionfinish(session, exitstatus):
    del pytest.chathead
