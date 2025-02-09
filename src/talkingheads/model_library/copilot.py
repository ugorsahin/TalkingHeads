"""Class definition for Copilot client"""

import asyncio
import time
from pathlib import Path
from typing import Union

from nodriver import cdp
from ..base_browser import BaseBrowser
from ..utils import check_filetype, is_url

class CopilotClient(BaseBrowser):
    """
    PiClient class to interact with Pi.
    It helps you to connect to https://copilot.microsoft.com/.
    Apart from core functionality Copilot supports web search.
    It is not possible to regenerate a response by using Copilot
    """

    def __init__(self, **kwargs):
        super().__init__(
            client_name="Copilot",
            url="https://copilot.microsoft.com",
            credential_check=False,
            **kwargs,
        )

    async def login(self):
        """
        Performs the login process with the provided username and password.
        You don't need to login to use Pi

        This function operates on the login page.
        It finds and clicks the login button,
        fills in the email and password textboxes

        Args:
            username (str): The username to be entered.
            password (str): The password to be entered.

        Returns:
            bool : True
        """
        self.logger.info("Login is not provided for Copilot at the moment.")
        return True

    async def postload_custom_func(self) -> None:
        """Copilot requires to accept privacy terms, the cookie below provides the response."""
        # self.browser.add_cookie({"name": "BCP", "value": "AD=0&AL=0&SM=0"})
        await self.browser.get(self.url)
        time.sleep(1)

    async def is_ready_to_prompt(self) -> bool:
        """
        Checks if the Copilot is ready to be prompted.
        The indication for an ongoing message generation process
        is a disabled send button. The indication for no input is the same
        disabled button. Therefore we put a dummy dot into the textarea
        and we are left with the only reason for the button to be disabled,
        that is, a message being generated.

        Returns:
            bool : return if the system is ready to be prompted.
        """
        text_area = await self.find_or_fail(self.markers.textarea)
        await text_area.send_keys(".")
        await self.wait_until_appear(self.markers.disabled_send)
        await self.wait_until_disappear(self.markers.disabled_send)

        # Then, we clear the text area to make space for new interacton :)
        await self.clear_textarea()

        return True

    async def get_last_response(self) -> str:
        """Returns the last response in the chat view.

        Args:
            check_greeting (bool):
                If set, checks the greeting message, provided after clicking New Topic.

        Returns:
            str: The last generated response
        """

        # If New topic button is clicked, the new message will be in different structure,
        # failing the last check below. If check_greeting is set,
        # we can return the text of this greeting element, instead of parsing the response.

        await self.wait_until_appear(self.markers.chatbox)

        resp = await self.find_or_fail(self.markers.chatbox, return_type="last")
        if not resp:
            return ""

        return resp.text_all

    async def upload_image(self, image_path: Union[str, Path]) -> bool:
        """Upload an image or a url and wait until it is uploaded,
        then returns.

        Args:
            action_bar (ShadowRoot): Action bar shadow root to find sub elements.
            image_path (str): the file path to image or the url.

        Returns:
            bool: True if the image loaded properly, False otherwise
        """
        if isinstance(image_path, Path):
            image_path = str(image_path)
        url = is_url(image_path)
        file = Path(image_path).exists() and check_filetype(image_path, self.markers.file_types)

        if not (url or file):
            self.logger.warning("Given path is neither an image path nor a url")
            return False

        im_input_element = await self.find_or_fail(self.markers.upload_img)
        await im_input_element.send_file(image_path)

        discard_button = await self.wait_until_appear(self.markers.dismiss, fail_ok=True)
        return discard_button is not None

    async def remove_attached_image(self) -> bool:
        """Removes the attached image from prompt

        Returns:
            bool: True if the action is valid
        """
        discard_button = await self.find_or_fail(self.markers.dismiss)
        if discard_button:
            self.logger.info("Clicking remove image button")
            await discard_button.click()
            return True

        return False

    async def interact(self, prompt: str, image_path: Union[str, Path] = None) -> str:
        """Sends a prompt and retrieves the response from the Copilot system.

        This function interacts with the Copilot.
        It takes the prompt as input and sends it to the system.
        The prompt may contain multiple lines separated by '\\n'.
        In this case, the function simulates pressing SHIFT+ENTER for each line.
        Upon arrival of the interaction, the function waits for the response.
        Once the response is ready, the function will return the response.

        Args:
            prompt (str): The interaction text.
            image_path (str, Optional): The path to image from local, or the url of the image.

        Returns:
            Dict[str]: The generated response.
        """

        text_area = await self.find_or_fail(self.markers.textarea)

        if not text_area:
            self.logger.error("Unable to locate text area, interaction fails.")
            return ""
        if image_path:
            uploaded = await self.upload_image(image_path)
            if not uploaded:
                self.logger.error('Image upload failed.')
                return ""

        prompt = prompt.replace("\n", "\r\n")
        await text_area.focus()
        await self.tab.send(cdp.input_.insert_text(text=prompt))

        send_button = await self.find_or_fail(self.markers.send)
        await send_button.click()

        if not await self.is_ready_to_prompt():
            self.logger.info("Cannot retrieve the response, something is wrong")
            return ""

        text = await self.get_last_response()
        self.logger.info("response is ready")
        self.log_chat(prompt=prompt, response=text)
        return text

    async def clear_textarea(self, wait_duration=0.3):
        """Waits a little and clears the input. By waiting, it avoids
        any inconvenience caused by rendering

        Args:
            wait_duration (float, optional): the waiting time before acting. Defaults to 0.3.
        """
        time.sleep(wait_duration)
        text_area = await self.find_or_fail(self.markers.textarea)
        await BaseBrowser.clear_input(text_area)
        return

    async def reset_thread(self) -> bool:
        """
        Function to close the current thread and start new one

        Returns:
            bool: False always, it is not possible to reset in Pi.
        """

        # Find home button, but it may be fine even the button is not there.
        open_menu_button = await self.find_or_fail(self.markers.open)
        if not open_menu_button:
            return False

        await open_menu_button.mouse_click()

        # Find new chat button.
        new_chat_button = await self.wait_until_appear(self.markers.new_chat)
        if not new_chat_button:
            return False
        await new_chat_button.mouse_click()
        await self.clear_textarea()
        await asyncio.sleep(0.3)

        return True

    async def regenerate_response(self):
        raise NotImplementedError("Copilot doesn't provide response regeneration")

    async def toggle_think_deeper(self):
        search_button = await self.find_or_fail(self.markers.think)
        await search_button.click()
        search_button = await self.find_or_fail(self.markers.think_active)
        return search_button is not None

    # async def close_location_modal(self):
    #     maybe_later = await self.find_or_fail(self.markers.location, fail_ok=True)
    #     if maybe_later:
    #         maybe_later.click()
