"""Class definition for HuggingChat client"""

import os
import time
from .. import BaseBrowser


class HuggingChatClient(BaseBrowser):
    """
    HuggingChatClient class to interact with HuggingChat.
    It helps you to conncet to https://huggingface.co/chat/ and login.
    Apart from core functionality HuggingChat supports web search.
    It is not possible to regenerate a response by using HuggingChat
    """

    def __init__(self, **kwargs):
        super().__init__(
            client_name="HuggingChat",
            url="https://huggingface.co/chat/",
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

        # Find login button, click it
        login_button = await self.wait_until_appear(self.markers.login)
        await login_button.click()
        self.logger.info("Clicked login button")

        # Find email textbox, enter e-mail
        email_box = await self.wait_until_appear(self.markers.username)
        await email_box.send_keys(os.environ.get(self.uname_var))
        self.logger.info("Filled username/email")

        # Find password textbox, enter password
        pass_box = await self.wait_until_appear(self.markers.password)
        await pass_box.send_keys(os.environ.get(self.pwd_var))
        self.logger.info("Filled password box")

        await pass_box.send_keys('\r\n')

        # Click continue
        await self.wait_until_appear(self.markers.textarea)
        return True

    async def interact(self, prompt: str):
        """Sends a prompt and retrieves the response from the HuggingChat system.

        This function interacts with the HuggingChat.
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

        time.sleep(0.5)
        send_button = await self.find_or_fail(self.markers.send)
        await send_button.click()
        self.logger.info("Message sent, waiting for response")

        await self.wait_until_disappear(self.markers.stop_gen)
        response = await self.get_last_response()
        if not response:
            return ""

        self.logger.info("response is ready")
        self.log_chat(prompt=prompt, response=response)
        return response

    async def reset_thread(self) -> bool:
        """Function to close the current thread and start new one"""
        await self.browser.get(self.url)
        return True

    async def toggle_search_web(self) -> bool:
        """Function to enable/disable web search feature"""
        search_web_toggle = await self.find_or_fail(self.markers.search)
        if not search_web_toggle:
            return False
        await search_web_toggle.click()
        
        # Find the button once more, this time to retrieve status
        search_web_toggle = await self.find_or_fail(self.markers.search)
        status = search_web_toggle.text_all
        status = "Search" in status
        self.logger.info("Search web is %s", ["disabled", "enabled"][status])
        return status

    async def switch_model(self, model_name: str) -> bool:
        """
        Switch the model.

        Args:
            model_name: str = The name of the model

        Returns:
            bool: True on success, False on fail
        """
        model_button = await self.find_or_fail(self.markers.models)
        if not model_button:
            return False
        await model_button.click()

        await self.wait_until_appear(self.markers.model_li)
        models = await self.find_or_fail(self.markers.model_li, return_type="all")

        if not models:
            return False

        models = {m.href.replace("/chat/models/", "").strip(): m for m in models}

        successful_switch = False
        model = models.get(model_name, None)
        if model is None:
            self.logger.error("Model %s has not found", model_name)
            self.logger.error("Available models are: %s", str(models.keys()))
            successful_switch = False
        else:
            await model.click()
            self.logger.info("Clicked model card %s", model_name)
            successful_switch = True

        if successful_switch is False:
            close_button = await self.find_or_fail(self.markers.model_a, fail_ok=True)
            if close_button:
                await close_button.click()

        return successful_switch

    async def regenerate_response(self):
        raise NotImplementedError("HuggingChat doesn't provide response regeneration")
