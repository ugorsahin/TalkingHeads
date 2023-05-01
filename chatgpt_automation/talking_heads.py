import time
from .chatgpt_client import ChatGPT_Client

class TalkingHeads:
    """An interface for talking heads"""
    def __init__(self, username: str, password: str, headless=False, head_count=2):
        self.head_count=head_count
        self.driver = ChatGPT_Client(username, password, headless)
        for _ in range(head_count-1):
            self.driver.browser.execute_script(
                '''window.open("https://chat.openai.com/chat","_blank");''')
            time.sleep(1)

        self.head_responses = [[] for _ in range(head_count)]

    def switch_to_tab(self, idx: int = 0):
        "Switch to tab"
        windows = self.driver.browser.window_handles
        if idx > len(windows):
            print(f"There is no tab with index {idx}")
            return
        self.driver.browser.switch_to.window(windows[idx])

    def interact(self, head_number, question):
        """interact with the given head"""
        self.switch_to_tab(head_number)
        response = self.driver.interact(question)
        return response

    def reset_all_threads(self):
        """reset heads for the given number"""
        for head in range(self.head_count):
            self.switch_to_tab(head)
            self.driver.reset_thread()

    def start_conversation(self, text_1: str, text_2: str, use_response_1: bool= True):
        """Starts a conversation between two heads"""
        assert len(self.head_count) >= 2, "At least 2 heads is neccessary for a conversation"

        f_response = self.interact(0, text_1)
        text_2 = text_2 + f_response if use_response_1 else text_2
        s_response = self.interact(1, text_2)

        self.head_responses[0].append(f_response)
        self.head_responses[1].append(s_response)

        return f_response, s_response

    def continue_conversation(self, text_1: str= None, text_2: str= None):
        """Make another round of conversation.
        If text_1 or text_2 is given, the response is not used"""
        text_1 = text_1 or self.head_responses[1][-1]

        f_response = self.interact(0, text_1)
        text_2 = text_2 or f_response

        s_response = self.interact(1, text_2)

        self.head_responses[0].append(f_response)
        self.head_responses[1].append(s_response)
        return f_response, s_response
