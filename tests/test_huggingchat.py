'''HuggingChat test'''

import time
import pytest
from selenium.webdriver.common.by import By
from talkingheads import HuggingChatClient

def test_start():
    pytest.chathead = HuggingChatClient(
        headless=True,
        verbose=True
    )
    assert pytest.chathead.ready, 'The Client is not ready'

def test_model_selection():
    assert pytest.chathead.switch_model('meta-llama/Llama-2-70b-chat-hf'), 'Model switch failed.'

def test_interaction():
    time.sleep(1)
    answer = pytest.chathead.interact('Without any explanation or extra information, just repeat the following: book.')
    assert 'book' in answer.lower(), f'Answer is not "book.", instead it returned {answer}'

def test_reset():
    assert pytest.chathead.reset_thread()
    assert len(pytest.chathead.browser.find_elements(By.XPATH, pytest.chathead.markers.chatbox_xq)) == 0, 'Chat is not empty'

def pytest_sessionfinish(session, exitstatus):
    del pytest.chathead
