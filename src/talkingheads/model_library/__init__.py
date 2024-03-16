"""Model inits"""

from .chatgpt import ChatGPTClient
from .claude import ClaudeClient
from .copilot import CopilotClient
from .gemini import GeminiClient
from .huggingchat import HuggingChatClient
from .lechat import LeChatClient
from .pi import PiClient


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


__all__ = [
    "ChatGPTClient",
    "ClaudeClient",
    "CopilotClient",
    "GeminiClient",
    "HuggingChatClient",
    "LeChatClient",
    "PiClient",
]
