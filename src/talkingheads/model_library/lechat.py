"""Class definition for LeChat client"""
import time

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

    def login(self, username: str, password: str):
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
        email_box = self.wait_until_appear(By.XPATH, self.markers.username_xq)
        email_box.send_keys(username)
        self.logger.info("Filled username/email")

        # Find password input area, enter password
        pass_box = self.wait_until_appear(By.XPATH, self.markers.password_xq)
        pass_box.send_keys(password)
        self.logger.info("Filled password box")

        pass_box.send_keys(Keys.ENTER)

        return True

    def get_last_response(self, tick_time : int = 200, tick_period : float = 0.5) -> str:
        """Retrieves the last response given by ChatGPT

        Returns:
            str: The last response
        """
        self.logger.info("Checking the response")
        self.wait_until_appear(By.XPATH, self.markers.chatbox_xq)
        # self.wait_until_disappear(By.XPATH, self.markers.stop_gen_xq)

        for _ in range(tick_time):
            time.sleep(tick_period)
            l_response = self.find_or_fail(
                By.XPATH, self.markers.chatbox_xq, return_type="last"
            ).text
            if l_response and l_response == self.interim_response:
                break
            self.interim_response = l_response

        if not self.interim_response:
            self.logger.error("There is no response, something is wrong")
            return ""

        self.logger.info("response is ready")
        return self.interim_response


    def interact(self, prompt: str):
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

        text_area = self.find_or_fail(By.XPATH, self.markers.textarea_xq)
        if not text_area:
            return ""

        for each_line in prompt.split("\n"):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)
        self.logger.info("Message sent, waiting for response")
        self.last_prompt = prompt
        response = self.get_last_response()
        if not response:
            return ""
        self.logger.info("response is ready")
        self.log_chat(prompt=prompt, response=response)
        return response

    def reset_thread(self):
        """Function to close the current thread and start new one"""
        self.browser.get(self.url)
        return True

    def switch_model(self, model_name: str):
        """
        Switch the model.

        Args:
            model_name: str = The name of the model

        Returns:
            bool: True on success, False on fail
        """
        model_button = self.find_or_fail(By.XPATH, self.markers.model_xq)
        if not model_button:
            return False
        model_button.click()

        models = self.find_or_fail(
            By.XPATH, self.markers.model_op_xq, return_type="all"
        )
        if not models:
            return False
        models = {m.text.split("\n")[0]: m for m in models}

        model = models.get(model_name, None)
        if model is None:
            self.logger.error("Model %s has not found", model_name)
            self.logger.error("Available models are: %s", str(models.keys()))
            model_button.click()
            return False

        model.click()
        self.logger.info("Switched to %s", model_name)
        return True

    def regenerate_response(self):
        regen_button = self.find_or_fail(By.XPATH, self.markers.regen_xq)
        if not regen_button:
            return ""
        regen_button.click()
        self.logger.info("Clicked regenerate button")

        response = self.get_last_response()
        if not response:
            return ""
        self.log_chat(response=response, regenerated=True)
        return response
