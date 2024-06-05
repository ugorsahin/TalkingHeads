"""Multiagent"""

import time
import logging
from datetime import datetime
from collections import OrderedDict
from typing import Any, Callable, Dict, List, Tuple, Union
from concurrent.futures.thread import ThreadPoolExecutor
from random import random, randint

import yaml
import pandas as pd
from mergedeep import merge
import emoji
from .. import (
    ChatGPTClient, ClaudeClient, CopilotClient, GeminiClient,
    HuggingChatClient, LeChatClient, PiClient
)
from ..base_browser import BaseBrowser
from ..utils import save_func_map

def get_client(client_name):
    """Returns the client by their tag name"""
    return {
        "ChatGPT": ChatGPTClient,
        "Claude": ClaudeClient,
        "Copilot": CopilotClient,
        "Gemini": GeminiClient,
        "HuggingChat": HuggingChatClient,
        "LeChat": LeChatClient,
        "Pi": PiClient,
    }.get(client_name, None)

class MultiAgent:
    """An interface to use multiple instances together."""

    def __init__(self, configuration_path: str):
        with open(configuration_path) as fd:
            self.config = yaml.safe_load(fd)

        ma_settings = self.config.get("multiagent_settings")
        if ma_settings:
            self.auto_save = ma_settings.get("auto_save") or False
            self.save_path = ma_settings.get("save_path") or None

        if self.auto_save:
            self.chat_history = pd.DataFrame(columns=["agent", "is_regen", "content"])
            self.set_save_path(self.save_path)

        self.logger = logging.getLogger('root')
        verbose = self.config["driver_settings"].get("shared").get("verbose")
        if verbose and not self.logger.isEnabledFor(logging.INFO):
            self.logger.setLevel(logging.INFO)
            self.logger.info("Verbose mode active")

        self.agent_swarm = {}
        driver_settings = self.config["driver_settings"]
        shared_config = driver_settings.get("shared")
        nodes = driver_settings.get("nodes")

        self.agent_swarm = {
            vals.get("tag", key) : self.open_agent(
                key,
                merge(shared_config, vals, {"auto_save": False, "multihead": True}),
            )
            for key, vals in nodes.items()
        }
        self.ready = True
        self.logger.info("All models are successfully loaded")

    def __del__(self):
        self.agent_swarm.clear()
        if self.auto_save:
            self.save()

    @staticmethod
    def dictmap(lambda_func: Callable, dictionary: Dict) -> Dict[str, Any]:
        """Takes a lambda function which accepts two parameters,
        and returns a dictionary based on this lambda function

        Args:
            executor (ThreadPoolExecutor): Executer to carry parallel execution.
            lambda_func (Callable): the function to be applied each of dictionary items.
            dictionary (Dict): the dictionary of the the application.

        Returns:
            Dict[str, Any]: A dictionary in the form defined by lambda_func
        """
        with ThreadPoolExecutor() as executor:
            result = OrderedDict(executor.map(lambda_func, *zip(*dictionary.items())))
        return result

    def open_agent(self, client_name: str, config: Dict[str, str]) -> BaseBrowser:
        """Open the given client

        Args:
            client_name (str): The tag of the agent.
            config (Dict[str, str]): The config of the agent

        Returns:
            BaseBrowser: The agent object
        """
        time.sleep(random() * randint(1, 4))
        client_constructor = get_client(client_name)
        return client_constructor(**config)

    def set_save_path(self, save_path: str):
        """Sets the path to save the file

        Args:
            save_path (str): The saving path
        """
        self.save_path = save_path or datetime.now().strftime("%Y_%m_%d_%H_%M_%S.csv")
        self.file_type = save_path.split(".")[-1] if save_path else "csv"

    def interact(self, head_name: str, prompt: str) -> str:
        """interact with the given head"""
        client = self.agent_swarm[head_name]
        response = client.interact(prompt)
        self.log_chat(client_name=client.client_name, response=response)
        return response

    def broadcast(self, prompt: str, exclude: List[str] = None) -> Dict[str, str]:
        """Interacts with the agent swarm and returns back the results,
        before interacting, the agents defined in the exclude list will be removed.

        Args:
            prompt (str): The prompt to broadcast agents.
            exclude (List[str], optional): The list of agents to be excluded. Defaults to None.

        Returns:
            Dict[str, str]: A dictionary contains the responses of each included agent.
        """

        agents = self.agent_swarm
        if exclude is not None:
            agents = dict(filter(lambda kv: kv[0] not in exclude, agents.items()))

        self.log_chat(prompt=prompt)
        responses = self.dictmap(
            lambda agent_name, _: (
                agent_name,
                self.interact(agent_name, prompt),
            ),
            agents,
        )
        return responses

    def aggregate(
        self,
        agents: Union[str, List[str]],
        prompt: str,
        responses: Dict[str, str],
        reset_before_agg: bool = True,
    ):
        """This function
        - Feeds all the responses into the selected agent(s) to aggregation,

        - Returns the response(s)

        Some examples of the aggregation are:
        - Composing a new message

        - Selecting the best message

        - Selecting the worst message

        - Find the most reoccuring number

        - Check if all the responses are the semantically similar

        Not all chat models can read lengthy inputs, remind your chat models to keep it short!

        By default, it resets the conversation of aggregation agents,
        set reset_before_agg=False to disable this.

        It is possible to select one agent or multiple agents for aggregation.

        Args:
            agents (List[str]): The agents selected to aggregate responses.
            prompt (str): Aggregation prompt
            responses (Dict[str, str]): The responses in the dictionary form.
            reset_before_agg (bool, optional): If set, resets the chathead. Defaults to True.
        """

        exclude_agents = list(filter(lambda k: k not in agents, self.agent_swarm))
        responses = " \n".join(
            [f"{idx}: {response}" for idx, response in enumerate(responses.values())]
        )
        # Remove emojis
        responses = emoji.replace_emoji(responses, replace="")

        if reset_before_agg:
            self.reset_agents(agents)

        final_prompt = f"{prompt}\nHere are the options:\n{responses}"

        agg_response = self.broadcast(final_prompt, exclude=exclude_agents)

        return agg_response

    def broadcast_and_aggregate(
        self,
        prompt: str,
        agg_agents: Union[str, List[str]],
        agg_prompt: str,
        exclude_agg_agents=True,
        reset_before_agg=True,
    ) -> Dict[str, str]:
        """This function
        - Broadcasts the prompt into the agent swarm,

        - Feeds all the responses into the selected agent(s) to aggregation,

        - Returns the response(s)

        Not all chat models can read lengthy inputs, remind your chat models to keep it short!
        By default, it resets the conversation of aggregation agents,
        set reset_before_agg=False to disable this.
        By default, it excludes the aggregation agent from agent swarm to respond,
        set exclude_agg_agents=False if you want the aggregator to respond too.
        It is possible to select one agent for aggregation, or select more than one agent.

        Args:
            prompt (str): The prompt to pass on model swarm.
            agg_agents (str): The agents to aggregate given responses
            agg_prompt (str): The prompt to pass on master head to apply the aggregation.
            exclude_agg_agents (bool, optional): If set, aggregation agents will only utilized in
                the aggregation step.
            reset_before_agg (bool, optional): If set, resets the chathead. Defaults to True.

        Returns:
            Tuple(Dict[str, str], Dict[str, str]): The responses of the
            broadcasting and aggregation steps.
        """

        agg_agents = [agg_agents] if isinstance(agg_agents, str) else agg_agents
        exclude = agg_agents if exclude_agg_agents else None

        responses = self.broadcast(prompt, exclude=exclude)
        final_responses = self.aggregate(
            agents=agg_agents,
            prompt=agg_prompt,
            responses=responses,
            reset_before_agg=reset_before_agg,
        )

        return responses, final_responses

    def broadcast_and_vote(self, prompt: str, voting_prompt: str) -> Dict[str, str]:
        """
        This function
        - Broadcasts the prompt to all agents.

        - Combines all responses and broadcast voting objective appended with the
            responses received from agents to select the best option.

        - Returns the results.

        Args:
            prompt (str): The first prompt to be broadcasted to the agents
            voting_prompt (str): The voting objective to be broadcasted to the agents.

        Returns:
            Tuple(Dict[str, str], Dict[str, str]): The responses of the broadcasting
            and voting steps.
        """

        return self.broadcast_and_aggregate(
            prompt=prompt,
            agg_agents=self.agent_swarm,
            agg_prompt=voting_prompt,
            exclude_agg_agents=False,
        )

    def reset_agents(self, agents: List[str] = None) -> List[bool]:
        """This function resets the conversations of the given agents. If the agents is empty,
        it resets all of them.

        Note: Some chat bots doesn't have reset feature.

        Args:
            agents (List[str], optional): If given, only resets the given agents,
                if None, reset all agents. Defaults to None.

        Returns:
            List[bool]: The reset status of each agent
        """
        agents_to_reset = (
            list(map(self.agent_swarm.get, agents))
            if agents
            else self.agent_swarm.values()
        )
        with ThreadPoolExecutor() as executor:
            reset_status = executor.map(
                lambda agent: agent.reset_thread(),
                agents_to_reset,
            )
        return reset_status

    def log_chat(
        self,
        client_name: str = None,
        prompt: str = None,
        response: str = None,
        regenerated: bool = False,
    ) -> bool:
        """
        Log a chat interaction in the chat history.

        Args:
            prompt (str): The user's prompt to be logged.
            response (str): The response to the user's prompt to be logged.

        Returns:
            bool: True if the interaction is logged, False otherwise.
        """
        if not self.auto_save:
            return False

        if prompt:
            self.chat_history.loc[len(self.chat_history)] = [
                "user",
                regenerated,
                prompt,
            ]

        if response:
            self.chat_history.loc[len(self.chat_history)] = [
                client_name,
                regenerated,
                response,
            ]
        return True

    def save(self) -> bool:
        """Saves the conversation."""
        save_func = save_func_map.get(self.file_type, None)
        if save_func:
            save_func = getattr(self.chat_history, save_func)
            save_func(self.save_path)
            self.logger.info("File saved to %s", self.save_path)
            return True

        self.logger.error("Unsupported file type %s", self.file_type)
        return False

class Conversation(MultiAgent):
    """A special Multiagent setting where two agents carry a conversation"""
    def __init__(self, configuration):
        super().__init__(configuration)
        if len(self.agent_swarm.keys()) != 2:
            self.logger.error("Only two agents are allowed in a conversation")
            return

        self.head_1, self.head_2 = self.agent_swarm.keys()
        self.head_1_response = None
        self.head_2_response = None

    def start_conversation(
        self, intro_prompt_1: str, intro_prompt_2: str, use_response_1: bool = True
    ):
        """Starts a conversation between two heads

        Args:
            intro_prompt_1 (str): The instruction of the first head.
            intro_prompt_2 (str): The instruction of the second head.
            use_response_1 (bool): If set, the first response returned by the first head
                will be appended to the end of the instruction of the second head.

        Returns:
            Tuple[str]: The responses of the respective chat bots.
        """
        self.head_1_response = self.interact(self.head_1, intro_prompt_1)
        if use_response_1:
            intro_prompt_2 += f"\n{self.head_1_response}"
        self.head_2_response = self.interact(self.head_2, intro_prompt_2)

        return self.head_1_response, self.head_2_response

    def continue_conversation(self, prompt_1: str = None, prompt_2: str = None) -> Tuple[str]:
        """Make another round of conversation.
        If prompt_1 or prompt_2 is given, the response is not used

        Args:
            prompt_1 (str, optional): If set, this prompt will be used instead of 
                the last response provided by head 2. Defaults to None.
            prompt_2 (str, optional): If set, this prompt will be used instead of
                the last response provided by head 1. Defaults to None.

        Returns:
            Tuple[str]: The responses of the respective chat bots.
        """
        prompt_1 = prompt_1 or self.head_2_response
        self.head_1_response = self.interact(self.head_1, prompt_1)

        prompt_2 = prompt_2 or self.head_1_response
        self.head_2_response = self.interact(self.head_2, prompt_2)

        return self.head_1_response, self.head_2_response
