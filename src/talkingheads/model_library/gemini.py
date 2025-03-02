"""Class definition for GeminiClient"""

import time
from typing import Union
from pathlib import Path
 
from talkingheads.base_browser import BaseBrowser
from ..utils import check_filetype


class GeminiClient(BaseBrowser):
    """GeminiClient class to interact with Gemini"""

    def __init__(self, **kwargs):
        super().__init__(
            client_name="Gemini",
            url="https://gemini.google.com/app",
            credential_check=False,
            **kwargs,
        )

    async def login(self) -> bool:
        """
        Performs the login process with the provided username and password.

        This function operates on the login page.
        It finds and clicks the login button,
        fills in the email and password textboxes

        Args:
            username (str): The username to be entered.
            password (str): The password to be entered.

        Returns:
            bool : True if login succesful, False otherwise.
        """
        self.logger.info(
            "It is not possible to provide login functionality for Google"
            "Please follow the instructions on the repo to connect Gemini"
        )
        text_area = await self.wait_until_appear(self.markers.textarea)
        if not text_area and not self.headless:
            for _ in range(5):
                self.logger.error(
                    """Prompt area can\'t located, use browser to manually
                    login your account, navigate to %s
                    and press any key here.""",
                    self.url,
                )
                input()
                text_area = await self.find_or_fail(self.markers.textarea)
                break
            else:
                self.logger.error("Login is unsuccesful")
                return False
        return True

    async def postload_custom_func(self):
        self.tab = await self.browser.get(self.url)

    async def get_response(
        self, tick_step: int = 40, tick_period: float = 0.5, max_same_ans: int = 3
    ) -> str:
        """Get the response from chat board

        Returns:
            str: The interaction text
        """
        self.logger.info("Message sent, waiting for response")
        self.interim_response = None
        await self.wait_until_appear(self.markers.chatbox)
        counter = 0
        for _ in range(tick_step):
            time.sleep(tick_period)
            l_response = await self.find_or_fail(
                self.markers.chatbox, return_type="last"
            )
            l_response = l_response.text_all
            if l_response:
                if l_response == self.interim_response:
                    counter += 1
                else:
                    counter = 0
            if counter > max_same_ans:
                break
            self.interim_response = l_response

        if not self.interim_response:
            self.logger.error("There is no response, something is wrong")
            return ""

        self.logger.info("response is ready")
        return self.interim_response

        # return response.text

    async def upload_file(self, file_path: Union[str, Path]) -> bool:
        """Upload an image or a url and wait until it is uploaded,
        then returns.

        Args:
            file_path (Union[str, Path]): the file path to image or the url.

        Returns:
            bool: True if the image loaded properly, False otherwise.
        """
        if isinstance(file_path, Path):
            file_path = str(file_path)
        file_type = check_filetype(file_path, self.markers.file_types)
        if not file_type:
            self.logger.error(
                "File type should be one of the following: %s",
                ", ".join(self.markers.file_types),
            )
            return False
        add_button = await self.find_or_fail(self.markers.add_btn)
        if not add_button:
            return False

        await add_button.click()
        input_xpath = self.markers.file_input.format(file_type=file_type)
        im_input_element = await self.find_or_fail(
            input_xpath,
            fail_ok=True
        )

        if not im_input_element:
            # Input element only appears when we click the image button
            # However, clicking this button will open file upload dialog,
            # and driver can't close that dialog. As a workaround,
            # we disable the click event on input element and then click the
            # button, so that we avoid opening the dialog but the
            # input element is safely loaded.
            await self.tab.evaluate("HTMLInputElement.prototype.click = function(){}")
            im_button = await self.find_or_fail(self.markers.img_btn)
            if not im_button:
                return False
            await im_button.mouse_click()

            # Check if there is a modal, click True if there is
            got_it_button = await self.find_or_fail(self.markers.got_it, fail_ok=True)
            if got_it_button:
                await got_it_button.click()
                time.sleep(0.3)
                await im_button.mouse_click()

            im_input_element = await self.wait_until_appear(input_xpath)
            if not im_input_element:
                return False

        if not im_input_element:
            self.logger.error("Can't find input element")
            return False

        await im_input_element.send_file(file_path)
        uploaded = await self.wait_until_appear(self.markers.img_loaded)
        if not uploaded:
            self.logger.error("Image upload failed.")
            return False

        self.logger.info("Image uploaded.")
        return True

    async def interact(self, prompt: str, image_path: Union[str, Path] = None) -> str:
        """
        Sends a prompt and retrieves the response from the ChatGPT system.

        This function interacts with the Gemini.
        It takes the prompt as input and sends it to the system.
        The prompt may contain multiple lines separated by '\\n'.
        In this case, the function simulates pressing SHIFT+ENTER for each line.
        Upon arrival of the interaction, the function waits for the response.
        Once the response is ready, the function will return the response.

        Args:
            prompt (str): The interaction text.
            image_path (str, optional): The image path for multimodal functionality
        Returns:
            str: The generated response.
        """
        if image_path:
            uploaded = await self.upload_file(image_path)
            if not uploaded:
                return ""

        text_area = await self.find_or_fail(self.markers.textarea)
        if not text_area:
            return ""
        for each_line in prompt.split("\n"):
            await text_area.send_keys(each_line)
            await text_area.send_keys("\r\n")

        send_button = await self.find_or_fail(self.markers.send)
        await send_button.click()

        response = await self.get_response()
        if not response:
            return ""
        self.last_prompt = prompt
        self.log_chat(prompt=prompt, response=response)
        return response

    async def reset_thread(self) -> bool:
        """Function to close the current thread and start new one

        Returns:
            bool: True new chat button is clicked, false otherwise
        """
        new_chat_button = await self.find_or_fail(self.markers.new_chat)
        if not new_chat_button:
            return False
        await new_chat_button.click()

        dialog_confirm = await self.find_or_fail(self.markers.chat_conf, fail_ok=True)
        if dialog_confirm:
            await dialog_confirm.click()
            self.logger.info("Confirmed New Chat in dialog window")

        time.sleep(0.5)
        responses = await self.find_or_fail(
            self.markers.chatbox, fail_ok=True, return_type="all"
        )
        if responses and len(responses) > 0:
            self.logger.error("Couldn't reset the chat")
            return False

        self.logger.info("New chat is ready")
        return True

    async def regenerate_response(self) -> str:
        """Closes the current thread and starts a new one.

        Args:
            None

        Returns:
            str: The regenerated response or empty string in case of failure.
        """
        regen_button = await self.find_or_fail(self.markers.regen)
        if not regen_button:
            return ""
        regen_button.click()
        self.logger.info("Clicked regeneration button")

        response = await self.get_response()
        self.logger.info("New response is ready")

        self.log_chat(response=response, regenerated=True)
        return response

    async def switch_model(self, model_name: str) -> bool:
        self.logger.info("Gemini doesn't have a model selection")
        return False
