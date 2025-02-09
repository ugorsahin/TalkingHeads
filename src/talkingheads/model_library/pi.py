"""Class definition for PI client"""
import asyncio
import re

from nodriver import cdp
from ..base_browser import BaseBrowser


class PiClient(BaseBrowser):
    """
    PiClient class to interact with Pi.
    It helps you to conncet to https://pi.ai/.
    Apart from core functionality Pi supports web search.
    It is not possible to regenerate a response by using Pi
    """

    def __init__(self, **kwargs):
        super().__init__(
            client_name="Pi",
            url="https://pi.ai/talk",
            credential_check=False, 
            skip_login=True,
            **kwargs
        )

    async def login(self):
        """
        Login is not provided for Pi at the moment.

        Returns:
            bool : False
        """
        self.logger.info("Login is not provided for Pi at the moment.")
        return False

    async def postload_custom_func(self) -> None:
        """Pi starts with a welcome message, we should wait until the message to finish."""
        await asyncio.sleep(0.5)
        await self.browser.get(self.url)
        await asyncio.sleep(0.5)

    async def is_ready_to_prompt(self) -> bool:
        """
        Checks if the Pi is ready to be prompted.
        The indication for an ongoing message generation process
        is a disabled send button. The indication for no input is the same
        disabled button. Therefore we put a dummy dot into the textarea
        and we are left with the only reason for the button to be disabled,
        that is, a message being generated.

        Returns:
            bool : return if the system is ready to be prompted.
        """

        text_area = await self.wait_until_appear(self.markers.textarea)
        if not text_area:
            return False
        await text_area.send_keys(".")
        await self.wait_until_disappear(self.markers.wait)

        # Then, we clear the text area to make space for new interacton :)
        await BaseBrowser.clear_input(text_area)
        return True

    async def interact(self, prompt: str):
        """Sends a prompt and retrieves the response from the ChatGPT system.

        This function interacts with the PI.
        It takes the prompt as input and sends it to the system.
        The prompt may contain multiple lines separated by '\\n'.
        In this case, the function simulates pressing SHIFT+ENTER for each line.
        Upon arrival of the interaction, the function waits for the response.
        Once the response is ready, the function will return the response.

        Args:
            prompt (str): The interaction text.

        Returns:
            str: The generated response.
        """

        text_area = await self.find_or_fail(self.markers.textarea)
        if not text_area:
            return ""

        for each_line in prompt.split("\n"):
            await text_area.send_keys(each_line)
            await text_area.send_keys("\r\n")

        send_button = await self.find_or_fail(self.markers.send)
        await send_button.click()
        self.logger.info("Message sent, waiting for response")

        if not await self.is_ready_to_prompt():
            return False

        response = await self.find_or_fail(self.markers.chatbox, return_type="last")

        if not response:
            return ""

        self.logger.info("response is ready")

        # Pi responses have double whitespaces between words.
        response = re.sub(r"\s+", ' ', response.text_all)
        return response

    async def reset_thread(self) -> bool:
        """
        Function to close the current thread and start new one

        Returns:
            bool: True if chatbox is None, False otherwise.
        """
        await self.tab.send(cdp.network.clear_browser_cookies())
        await self.browser.get(self.url)
        await self.postload_custom_func()
        await self.wait_until_appear(self.markers.textarea)
        chatbox = await self.find_or_fail(self.markers.chatbox, fail_ok=True, return_type='all')
        return len(chatbox) == 1

    async def regenerate_response(self):
        raise NotImplementedError("Pi doesn't provide response regeneration")
