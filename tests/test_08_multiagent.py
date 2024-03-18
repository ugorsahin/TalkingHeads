"""ChatGPT test"""

import os
import re
from pathlib import Path

import psutil
import pytest
from talkingheads import MultiAgent


def test_start():
    # 3 heads: ChatGPT, LeChat and Pi
    config_path = Path(os.path.dirname(__file__)) / "test_assets/multiagent_cfg.yaml"
    pytest.multihead = MultiAgent(config_path)
    assert pytest.multihead.ready, "The Client is not ready"


def test_seperate_broadcast_aggregate():
    responses = pytest.multihead.broadcast(
        "Without any explanation or extra information, just repeat the following: book."
    )
    assert all(head_name in responses for head_name in ["ChatGPT", "LeChat", "Pi"])
    assert all("book" in response.lower() for response in responses.values())

    agg_response = pytest.multihead.aggregate(
        agents="ChatGPT",
        prompt="Write 'indeed' if all the options below has the word 'book'",
        responses=responses,
    )
    assert (
        len(agg_response) == 1
    ), f"The number of results is not 1, {len(agg_response)}"
    response = agg_response.get("ChatGPT")
    assert (
        response is not None
    ), f"ChatGPT doesn't exist in aggregation responses, existing heads: {agg_response.keys()}"
    assert f"The word indeed doesn't exist in the response, instead it responded {response}"


def test_broadcast_and_aggregate():
    broadcast_responses, agg_responses = pytest.multihead.broadcast_and_aggregate(
        prompt="Provide a number between 0 and 1000. Write a proper sentence (for example, I selected X)",
        agg_agents="LeChat",
        agg_prompt="Select the highest number among options",
        exclude_agg_agents=False
    )
    convert_num = lambda x: int(re.search(r"\d+", x).group(0))
    assert (
        len(agg_responses) == 1
    ), f"The number of results is not 1, {len(agg_responses)}"
    response = agg_responses.get("LeChat")
    assert (
        response is not None
    ), f"LeChat doesn't exist in aggregation responses, existing heads: {agg_responses.keys()}"

    max_num = max(map(convert_num, broadcast_responses.values()))
    agg_max_num = convert_num(response)
    assert (
        max_num == agg_max_num
    ), "Calculated max num is {max_num}, aggregation response is {agg_max_num}"


def test_delete_multihead():
    del pytest.multihead
    assert not any(
        "undetected_chromedriver" in p.name() for p in psutil.process_iter()
    ), "Undetected chromedriver exists"
