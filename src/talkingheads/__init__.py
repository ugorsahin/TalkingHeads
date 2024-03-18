"""Initialization file of talkingheads library"""
from .base_browser import BaseBrowser
from .utils import is_url, check_filetype, detect_chrome_version
from .model_library import ChatGPTClient, ClaudeClient, CopilotClient, \
    GeminiClient, HuggingChatClient, LeChatClient, PiClient
from .multiagent.multiagent import MultiAgent, Conversation

__all__ = [
    "is_url",
    "check_filetype",
    "detect_chrome_version",
    "BaseBrowser",
    "ChatGPTClient",
    "ClaudeClient",
    "CopilotClient",
    "GeminiClient",
    "HuggingChatClient",
    "LeChatClient",
    "PiClient",
    "MultiAgent",
    "Conversation",
    "model_library",
    "multiagent"
]
