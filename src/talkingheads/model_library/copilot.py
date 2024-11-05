"""Class definition for Copilot client"""

import time
from pathlib import Path
from typing import Union

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

    def login(self, username: str = None, password: str = None):
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

    def postload_custom_func(self) -> None:
        """Copilot requires to accept privacy terms, the cookie below provides the response."""
        self.browser.add_cookie({"name": "BCP", "value": "AD=0&AL=0&SM=0"})
        self.browser.get(self.url)
        time.sleep(1)

    def is_ready_to_prompt(self) -> bool:
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
        text_area = self.find_or_fail(By.XPATH, self.markers.textarea_xq)
        text_area.send_keys(".")

        submit_button = self.find_or_fail(By.XPATH, self.markers.submit_xq)
        if not submit_button:
            return False

        self.wait_object.until(EC.element_to_be_clickable(submit_button))

        # Then, we clear the text area to make space for new interacton :)
        text_area.send_keys(Keys.CONTROL + "a", Keys.DELETE)
        return True

    def get_last_response(self) -> str:
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

        resp = self.find_or_fail(By.XPATH, self.markers.answer_xq, return_type="last")
        if not resp:
            return ""

        return resp.text

    def upload_image(self, image_path: Union[str, Path]) -> bool:
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

        im_input_element = self.find_or_fail(By.XPATH, self.markers.img_upload_xq)
        im_input_element.send_keys(image_path)

        condition = EC.element_to_be_clickable((By.XPATH, self.markers.dismiss_xq))
        WebDriverWait(self.browser, 10).until(condition)
        return True

    def remove_attached_image(self) -> bool:
        """Removes the attached image from prompt

        Returns:
            bool: True if the action is valid
        """
        discard_button = self.find_or_fail(By.XPATH, self.markers.dismiss_xq)
        if discard_button:
            self.logger.info("Clicking remove image button")
            discard_button.click()
            return True

        return False

    def interact(self, prompt: str, image_path: Union[str, Path] = None) -> str:
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

        text_area = self.find_or_fail(By.XPATH, self.markers.textarea_xq)

        if not text_area:
            self.logger.error("Unable to locate text area, interaction fails.")
            return ""
        if image_path:
            self.upload_image(image_path)

        for each_line in prompt.split("\n"):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)

        # Click enter and send the message
        text_area.send_keys(Keys.ENTER)

        self.close_location_modal()
        if image_path:
            time.sleep(1)

        if not self.is_ready_to_prompt():
            self.logger.info("Cannot retrieve the response, something is wrong")
            return ""

        text = self.get_last_response()
        self.logger.info("response is ready")
        self.log_chat(prompt=prompt, response=text)
        return text

    def reset_thread(self) -> bool:
        """
        Function to close the current thread and start new one

        Returns:
            bool: False always, it is not possible to reset in Pi.
        """

        # Find home button, but it may be fine even the button is not there.
        home_button = self.find_or_fail(By.XPATH, self.markers.home_xq)
        if not home_button:
            self.logger.info("Home button is not found, trying view history button")
        else:
            home_button.click()

        # Find view history button to find new chat button.
        view_history_button = self.find_or_fail(By.XPATH, self.markers.history_xq)
        if not view_history_button:
            return False
        view_history_button.click()

        # Find new chat button.
        new_chat_button = self.find_or_fail(By.XPATH, self.markers.new_chat_xq)
        if not new_chat_button:
            return False
        new_chat_button.click()

        return True

    def regenerate_response(self):
        raise NotImplementedError("Copilot doesn't provide response regeneration")

    def close_location_modal(self):
        maybe_later = self.find_or_fail(By.XPATH, self.markers.location_xq, fail_ok=True)
        if maybe_later:
            maybe_later.click()
