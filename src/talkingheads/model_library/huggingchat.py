"""Class definition for HuggingChat client"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
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

        # Find login button, click it
        login_button = self.wait_until_appear(By.XPATH, self.markers.login_xq)
        login_button.submit()
        self.logger.info("Clicked login button")

        # Find email textbox, enter e-mail
        email_box = self.wait_until_appear(By.XPATH, self.markers.username_xq)
        email_box.send_keys(username)
        self.logger.info("Filled username/email")

        # Find password textbox, enter password
        pass_box = self.wait_until_appear(By.XPATH, self.markers.password_xq)
        pass_box.send_keys(password)
        self.logger.info("Filled password box")

        pass_box.send_keys(Keys.ENTER)

        # Click continue
        # a_login_button = self.wait_until_appear(By.XPATH, self.markers.a_login_xq)
        # a_login_button.click()
        # self.logger.info("Clicked login button")
        return True

    def interact(self, prompt: str):
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

        text_area = self.find_or_fail(By.XPATH, self.markers.textarea_xq)
        if not text_area:
            return ""

        for each_line in prompt.split("\n"):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)
        self.logger.info("Message sent, waiting for response")
        self.wait_until_disappear(By.XPATH, self.markers.stop_gen_xq)
        response = self.find_or_fail(
            By.XPATH, self.markers.chatbox_xq, return_type="last"
        )
        if not response:
            return ""
        self.logger.info("response is ready")
        self.log_chat(prompt=prompt, response=response.text)
        return response.text

    def reset_thread(self) -> bool:
        """Function to close the current thread and start new one"""
        self.browser.get(self.url)
        return True

    def toggle_search_web(self) -> bool:
        """Function to enable/disable web search feature"""
        search_web_toggle = self.find_or_fail(By.XPATH, self.markers.search_xq)
        if not search_web_toggle:
            return False
        search_web_toggle.click()
        status = search_web_toggle.get_attribute("aria-checked")
        status = status == "true"
        self.logger.info("Search web is %s", ["disabled", "enabled"][status])
        return status

    def switch_model(self, model_name: str) -> bool:
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

        self.wait_object.until(
            EC.presence_of_element_located((By.XPATH, self.markers.settings_xq))
        )
        models = self.find_or_fail(
            By.XPATH, self.markers.model_li_xq, return_type="all"
        )
        if not models:
            return False
        models = {m.text.strip(): m for m in models}

        successful_switch = True
        model = models.get(model_name, None)
        if model is None:
            self.logger.error("Model %s has not found", model_name)
            self.logger.error("Available models are: %s", str(models.keys()))
            successful_switch = False
        else:
            model.click()
            self.logger.info("Clicked model card %s", model_name)

            activate_button = self.find_or_fail(By.XPATH, self.markers.model_act_xq)
            if not activate_button:
                successful_switch = False
            else:
                activate_button.click()

        close_button = self.find_or_fail(By.XPATH, self.markers.model_a_xq, fail_ok=True)
        if close_button:
            close_button.click()

        return successful_switch

    def regenerate_response(self):
        raise NotImplementedError("HuggingChat doesn't provide response regeneration")
