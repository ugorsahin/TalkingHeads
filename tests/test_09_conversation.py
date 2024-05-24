"""Conversation test"""
import os
from pathlib import Path
# import psutil

import pytest

from talkingheads.multiagent import Conversation


def test_start():
    config_path = Path(os.path.dirname(__file__)) / "test_assets/conversation_cfg.yaml"
    pytest.multihead = Conversation(config_path)
    assert pytest.multihead.ready, "The Client is not ready"


def test_start_conversation():
    # How to check if given answers are correct?
    interviewer = """Assume you are a researcher and will conduct a human cognition test.
    Instruct the subject with the following instructions, one by one. Only ask for one instruction at a time.
    Here are the instructions
    1) Without further ado, just write the following: "Book."
    2) Calculate 4x10.
    3) Name three countries with the largest total area in North America.

    Start by greeting the subject."""

    candidate = (
        "You accepted participating in a research study "
        "and you will follow the instructions of the researchers."
        "Respond to the questions with full and grammatically correct sentences."
    )

    response = pytest.multihead.start_conversation(
        intro_prompt_1=interviewer, intro_prompt_2=candidate
    )
    assert len(response) == 2, "There are more than two answers"
    assert len(response[0]), "First answer is empty"
    assert len(response[1]), "Second answer is empty"
    assert "book" in response[0].lower(), "The word book is absent in first response"
    assert "book" in response[1].lower(), "The word book is absent in second response"


def test_continue_conversation():
    response = pytest.multihead.continue_conversation()
    assert len(response) == 2, "Round 1: There are more than two answers"
    assert len(response[0]), "Round 1: First answer is empty"
    assert len(response[1]), "Round 1: Second answer is empty"
    assert all(
        i in response[0] for i in ["4", "10"]
    ), "Round 1: The numbers 4 and 10 are absent in first response"
    assert "40" in response[1], "Round 1: The number 40 is absent in second response"

    response = pytest.multihead.continue_conversation()
    assert len(response) == 2, "Round 2: There are more than two answers"
    assert len(response[0]), "Round 2: First answer is empty"
    assert len(response[1]), "Round 2: Second answer is empty"
    assert (
        "north america" in response[0].lower()
    ), "Round 2: The keyword 'North America' is absent in first response"
    assert all(
        i in response[1].lower() for i in ["united states", "canada", "mexico"]
    ), "Round 2: The countries are wrong"

# def test_delete_chathead():
#     del pytest.multihead
#     assert not any(
#         "undetected_chromedriver" in p.name() for p in psutil.process_iter()
#     ), "Undetected chromedriver exists"
