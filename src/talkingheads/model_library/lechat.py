"""Class definition for LeChat client"""
import time
import os

import nodriver as nd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from ..base_browser import BaseBrowser


class LeChatClient(BaseBrowser):
    """
    LeChatClient class to interact with LeChat.
    It helps you to conncet to https://chat.mistral.ai/chat and login.
    It is not possible to regenerate a response by using LeChat
    """

    def __init__(self, **kwargs):
        super().__init__(
            client_name="LeChat",
            url="https://chat.mistral.ai/chat",
            **kwargs,
        )

    async def login(self):
        """
        Performs the login process with the provided username and password.

        This function operates on the login page.
        It finds and clicks the login button,
        fills in the email and password textboxes

        Args:
            username (str): The username to be entered.
            password (str): The password to be entered.

        Returns:
            bool : True if login is successful
        """

        # Find username input area, enter e-mail
        # Find email textbox, enter e-mail
        email_box = await self.wait_until_appear(self.markers.username)
        await email_box.send_keys(os.environ.get(self.uname_var))
        self.logger.info("Filled username/email")

        # Find password textbox, enter password
        pass_box = await self.wait_until_appear(self.markers.password)
        await pass_box.send_keys(os.environ.get(self.pwd_var))
        self.logger.info("Filled password box")

        verification_box = await self.wait_until_appear(self.markers.verify)
        if verification_box:
            verification_box.click()

        await pass_box.send_keys('\r\n')

        return True

    async def interact(self, prompt: str):
        """Sends a prompt and retrieves the response.

        This function interacts with the LeChat.
        It takes the prompt as input and sends it to the system.
        The prompt may contain multiple lines seperated by '\\n'.
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
            await text_area.send_keys('\r\n')

        send_button = await self.find_or_fail(self.markers.send)
        await send_button.click()

        self.logger.info("Message sent, waiting for response")
        self.last_prompt = prompt
        response = await self.get_last_response()
        if not response:
            return ""
        self.logger.info("response is ready")
        self.log_chat(prompt=prompt, response=response)
        return response

    async def reset_thread(self):
        """Function to close the current thread and start new one"""
        self.tab = await self.browser.get(self.url)
        return True

    async def regenerate_response(self):
        regen_button = await self.find_or_fail(self.markers.regen)
        if not regen_button:
            return ""
        await regen_button.click()
        self.logger.info("Clicked regenerate button")

        response = await self.get_last_response()
        if not response:
            return ""
        self.log_chat(response=response, regenerated=True)
        return response
