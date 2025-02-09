"""Class definition for DeepSeekClient"""

import re
import os
import time
from pathlib import Path
from typing import Union, Dict

import nodriver as nd
from .. import BaseBrowser

class DeepSeekClient(BaseBrowser):
    """DeepSeekClient class to interact with DeepSeek"""

    def __init__(self, **kwargs):
        super().__init__(
            client_name="DeepSeek", url="https://chat.deepseek.com", **kwargs
        )

    async def preload_custom_func(self):
        self.tab = await self.browser.get(self.url)

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
            None
        """

        # Find e-mail button
        email_box = await self.wait_until_appear(self.markers.username, 5)
        if not email_box:
            self.logger.error("Username area has not found")
            return False

        await email_box.send_keys(os.environ.get(self.uname_var))
        self.logger.info("Filled email box")

        # Find password textbox, enter password
        pass_box = await self.wait_until_appear(self.markers.password)
        if not pass_box:
            self.logger.error("Password area has not found")
            return False

        await pass_box.send_keys(os.environ.get(self.pwd_var))
        self.logger.info("Filled password box")

        checkbox = await self.wait_until_appear(self.markers.checkbox)
        if not checkbox:
            self.logger.error("Checkbox area has not found")

        await checkbox.click()
        self.logger.info("Checked password box")

        login_button = await self.wait_until_appear(self.markers.login)
        if not checkbox:
            self.logger.error("Login button has not found")

        await login_button.click()

        text_area = await self.wait_until_appear(self.markers.textarea)

        if text_area is None:
            self.logger.error("Login is not successful.")
            return False

        self.logger.info("Login is not successful.")
        return True

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

        input_element = self.find_or_fail(self.markers.input_file, fail_ok=True)
        input_element.send_keys(file_path)

        uploaded = await self.wait_until_appear(self.markers.img_loaded)
        if not uploaded:
            self.logger.error('Image upload failed.')
            return False

        self.logger.info('Image uploaded.')
        return True

    async def reset_thread(self) -> bool:
        """Function to close the current thread and start new one"""
        new_chat_button = await self.wait_until_appear(self.markers.new_chat)
        if not new_chat_button:
            self.logger.error("New chat button has not found.")
            return False
        await new_chat_button.click()

        self.logger.info(
            "New chat is available."
        )
        return True

    async def get_last_response(
        self, num_step: int = 200, period: float = 0.5, same_answer_limit=3
    ) -> str:

        self.logger.info("Checking the response")

        self.interim_response = None
        await self.wait_until_appear(self.markers.chatbox)

        same_answer = 0
        while not await self.find_or_fail(self.markers.disabled_send, fail_ok=True) and same_answer < same_answer_limit:
            time.sleep(period)
            l_response = await self.find_or_fail(self.markers.chatbox, return_type='last')
            l_response = l_response.text_all
            same_answer = [0, same_answer + 1][l_response == self.interim_response]

            self.interim_response = l_response
            if same_answer > same_answer_limit:
                break

        if not self.interim_response:
            self.logger.error("There is no response, something is wrong")
            return ""

        self.logger.info("response is ready")
        response = await self.response_parser()

        return response

    async def response_parser(self) -> Union[Dict[str, str], str]:
        # mathml_xpath = ".//*[local-name()='annotation']"
        data = {"response"  : "", "thought"   : ""}

        async def parse_katex(item):
            formula = await item.query_selector('annotation')
            return formula.text_all

        async def parse_element(item):
            if "class_" in item.attrs and "ds-markdown-math" in item.attrs["class_"]:
                return await parse_katex(item)

            if item.tag == "p":
                return ' '.join([
                    await parse_katex(child) if child.tag == 'span' else str(child)
                    for child in item.children
                ])

            if item.tag == "ul":
                return '\n'.join([
                    await parse_element(child.children[0])
                    for child in item.children
                ])

            return item.text_all

        parent_div = await self.find_or_fail(self.markers.chatbox, return_type="last")
        thought_regex = r"Thought for \d+ seconds\n"
        for child in parent_div.children:
            if "markdown" in child.attrs['class_']:
                text = "\n".join([
                    await parse_element(x)
                    for x in child.children
                ])
                data["response"] += text
            elif re.search(thought_regex, child.text_all):
                data["thought"] += child.text

        if data["thought"] == "":
            return data["response"]
        else:
            return data

    async def toggle_search(self):
        search_button = await self.find_or_fail(self.markers.search)
        await search_button.click()
        search_button = await self.find_or_fail(self.markers.search)
        return "transparent" not in search_button.attrs['style']

    async def toggle_deepthink(self):
        deepthink_button = await self.find_or_fail(self.markers.deepthink)
        await deepthink_button.click()
        deepthink_button = await self.find_or_fail(self.markers.deepthink)
        return "transparent" not in deepthink_button.attrs['style']
