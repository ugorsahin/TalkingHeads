"""This module implements the Conversation class,
a special multiagent designed to carry a conversation between two agents.
"""

from typing import Tuple
from ..multiagent import MultiAgent


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
