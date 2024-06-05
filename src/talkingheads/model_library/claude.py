"""Class definition for Claude client"""
import logging
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from ..base_browser import BaseBrowser


class ClaudeClient(BaseBrowser):
    """
    ClaudeClient class to interact with Claude.
    It helps you to conncet to https://claude.ai/.
    Apart from core functionality Claude supports web search.
    It is not possible to regenerate a response by using Claude
    """

    def __init__(self, **kwargs):
        super().__init__(
            client_name="Claude",
            url="https://claude.ai",
            credential_check=False,
            **kwargs,
        )

    def login(self, _1: str = None, _2: str = None) -> bool:
        """
        It is only possible to login Claude manually.

        Args:
            _1 (str): Unused parameter 1.
            _2 (str): Unused parameter 2.

        Returns:
            bool : True
        """
        logging.info("Login is not provided for Claude at the moment.")
        return True

    def postload_custom_func(self) -> bool:
        """In order to continue chat screen, a click on start button is required"""
        start_button = self.wait_until_appear(By.XPATH, self.markers.start_btn_xq)
        if not start_button:
            logging.error("Post-load has failed.")
            return False
        start_button.click()
        return True

    def is_ready_to_prompt(self) -> bool:
        """
        Checks if the Claude is ready to be prompted.
        The indication for an ongoing message generation process
        is a disabled send button. The indication for no input is the same
        disabled button. Therefore we put a dummy dot into the textarea
        and we are left with the only reason for the button to be disabled,
        that is, a message being generated.

        Returns:
            bool : return if the system is ready to be prompted.
        """
        text_area = self.find_or_fail(By.CLASS_NAME, self.markers.textarea_cq)
        text_area.send_keys(".")

        button = self.find_or_fail(By.XPATH, self.markers.send_button_xq)
        if not button:
            return False

        self.wait_object.until(EC.element_to_be_clickable(button))

        # Then, we clear the text area to make space for new interacton :)
        text_area.send_keys(Keys.CONTROL + "a", Keys.DELETE)
        return True

    def interact(self, prompt: str) -> str:
        """Sends a prompt and retrieves the response from the ChatGPT system.

        This function interacts with the Claude.
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

        text_area = self.find_or_fail(By.CLASS_NAME, self.markers.textarea_cq)

        if not text_area:
            logging.error("Unable to locate text area, interaction fails.")
            return ""

        for each_line in prompt.split("\n"):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)

        # Click enter and send the message
        text_area.send_keys(Keys.ENTER)

        if not self.is_ready_to_prompt():
            logging.info("Cannot retrieve the response, something is wrong")
            return ""

        response = self.find_or_fail(
            By.XPATH,
            self.markers.chatarea_xq,
            return_type="last",
        )
        if not response:
            return ""
        logging.info("response is ready")
        self.log_chat(prompt=prompt, response=response.text)
        return response.text

    def reset_thread(self) -> bool:
        """
        Function to close the current thread and start new one

        Returns:
            bool: True if reset is successful, false otherwise.
        """
        text_area = self.find_or_fail(By.CLASS_NAME, self.markers.textarea_cq)
        text_area.send_keys(Keys.CONTROL + "K")
        time.sleep(0.5)
        start_button = self.wait_until_appear(By.XPATH, self.markers.start_btn_xq)
        if not start_button:
            return False
        start_button.click()

        return True

    def switch_model(self, _: str) -> None:
        raise NotImplementedError("Claude only has one model")

    def regenerate_response(self) -> str:
        regen_button = self.find_or_fail(By.XPATH, self.markers.regen_xq)
        if not regen_button:
            return ""
        regen_button.click()

        if not self.is_ready_to_prompt():
            logging.info("Cannot retrieve the response, something is wrong")
            return ""

        response = self.find_or_fail(
            By.XPATH,
            self.markers.chatarea_xq,
            return_type="last",
        )
        if not response:
            return ""

        logging.info("response is ready")
        self.log_chat(response=response.text, regenerated=True)
        return response.text
