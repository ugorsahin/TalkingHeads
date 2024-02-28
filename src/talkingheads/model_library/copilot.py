"""Class definition for Copilot client"""

import logging
import re
from typing import Union, Dict

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from ..base_browser import BaseBrowser


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
            timeout_dur=30,
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
        logging.info("Login is not provided for Copilot at the moment.")
        return True

    def postload_custom_func(self) -> None:
        """Copilot requires to accept privacy terms, the cookie below provides the answer."""
        self.browser.add_cookie({"name": "BCP", "value": "AD=0&AL=0&SM=0"})
        self.browser.get(self.url)
        return

    def is_ready_to_prompt(self, text_area, shadow_element) -> bool:
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
        text_area.send_keys(".")

        button = self.find_or_fail(
            By.CLASS_NAME, self.markers.button_cq, dom_element=shadow_element
        )
        button = self.find_or_fail(By.TAG_NAME, "button", dom_element=button)
        if not button:
            return False

        self.wait_object.until(EC.element_to_be_clickable(button))

        # Then, we clear the text area to make space for new interacton :)
        text_area.send_keys(Keys.CONTROL + "a", Keys.DELETE)
        return True

    def get_last_answer(self, check_greeting: bool = False) -> str:
        """Returns the last response in the chat view.

        Args:
            check_greeting (bool): If set, checks the greeting message, provided after clicking New Topic.

        Returns:
            str: The last generated answer
        """

        # Shadow roots, aren't they amazing!
        main_area = self.find_or_fail(
            By.TAG_NAME, self.markers.main_area_tq, return_shadow=True
        )
        resp = self.find_or_fail(
            By.ID, self.markers.con_main_iq, dom_element=main_area, return_shadow=True
        )
        resp = self.find_or_fail(
            By.CSS_SELECTOR,
            self.markers.con_chat_sq,
            dom_element=resp,
            return_type="last",
            return_shadow=True,
        )
        resp = self.find_or_fail(
            By.CLASS_NAME,
            self.markers.con_resp_cq,
            dom_element=resp,
            return_shadow=True,
        )
        resp = self.find_or_fail(
            By.CSS_SELECTOR,
            self.markers.con_msg_sq,
            dom_element=resp,
            return_type="last",
            return_shadow=True,
        )
        resp = self.find_or_fail(
            By.CSS_SELECTOR, self.markers.con_ins_sq, dom_element=resp
        )
        # If New topic button is clicked, the new message will be in different structure,
        # failing the last check below. If check_greeting is set,
        # we can return the text of this greeting element, instead of parsing the response.
        if check_greeting:
            return resp.text

        resp = self.find_or_fail(
            By.CLASS_NAME, self.markers.con_last_cq, dom_element=resp, fail_ok=check_greeting
        )
        text = "".join([elem.text for elem in resp.children()])
        # Fix citations
        text = re.sub(r"\n(\d{1,2})", r"[\g<1>]", text)

        return text

    def interact(self, prompt: str) -> str:
        """Sends a prompt and retrieves the answer from the ChatGPT system.

        This function interacts with the PI.
        It takes the prompt as input and sends it to the system.
        The prompt may contain multiple lines separated by '\\n'.
        In this case, the function simulates pressing SHIFT+ENTER for each line.
        Upon arrival of the interaction, the function waits for the answer.
        Once the response is ready, the function will return the response.

        Args:
            prompt (str): The interaction text.

        Returns:
            Dict[str]: The generated answer.
        """
        main_area = self.find_or_fail(
            By.TAG_NAME, self.markers.main_area_tq, return_shadow=True
        )
        action_bar = self.find_or_fail(
            By.ID, self.markers.action_bar_iq, dom_element=main_area, return_shadow=True
        )
        input_bar = (
            self.find_or_fail(
                By.CLASS_NAME, self.markers.input_bar_cq, dom_element=action_bar
            )
            .children()[0]
            .shadow_root
        )
        text_area = self.find_or_fail(
            By.ID, self.markers.textarea_iq, dom_element=input_bar
        )

        if not text_area:
            logging.error("Unable to locate text area, interaction fails.")
            return ""

        for each_line in prompt.split("\n"):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)

        # Click enter and send the message
        text_area.send_keys(Keys.ENTER)

        if not self.is_ready_to_prompt(text_area, action_bar):
            logging.info("Cannot retrieve the answer, something is wrong")
            return ""

        text = self.get_last_answer()
        logging.info("Answer is ready")
        self.log_chat(prompt=prompt, answer=text)
        return text

    def reset_thread(self) -> bool:
        """
        Function to close the current thread and start new one

        Returns:
            bool: False always, it is not possible to reset in Pi.
        """
        main_area = self.find_or_fail(
            By.TAG_NAME, self.markers.main_area_tq, return_shadow=True
        )
        if not main_area:
            return False

        action_bar = self.find_or_fail(
            By.ID, self.markers.action_bar_iq, dom_element=main_area, return_shadow=True
        )
        if not action_bar:
            return False

        new_chat_button = self.find_or_fail(
            By.CLASS_NAME, self.markers.new_chat_cq, dom_element=action_bar
        )
        if not new_chat_button:
            return False
        new_chat_button.click()

        return True

    def get_models(self, get_active_model: bool =False) -> Union[Dict[str, WebElement], WebElement]:
        """
        Get the current model. (style)
        Args:
            get_active_model: bool = If set, returns the current element
        Returns:
            Dict[str, WebElement]: Dictionary of models and their element.
        """

        main_area = self.find_or_fail(
            By.TAG_NAME, self.markers.main_area_tq, return_shadow=True
        )

        con_area = self.find_or_fail(
            By.ID, self.markers.con_main_iq, dom_element=main_area, return_shadow=True
        )

        wel_area = self.find_or_fail(
            By.CSS_SELECTOR,
            self.markers.welcome_tq,
            dom_element=con_area,
            return_shadow=True,
        )

        tone_area = self.find_or_fail(
            By.CSS_SELECTOR,
            self.markers.tone_tq,
            dom_element=wel_area,
            return_shadow=True,
        )

        models = dict(
            map(
                lambda x: (x.text.split("\n")[-1], x),
                self.find_or_fail(
                    By.CSS_SELECTOR, "button", dom_element=tone_area, return_type="all"
                ),
            )
        )
        if get_active_model:
            active_model = [
                m_name for m_name, model in models.items()
                if model.get_attribute("aria-checked") == "true"
            ]
            return active_model[0]

        return models

    def switch_model(self, model_name: str) -> bool:
        """
        Switch the model. (style)

        Args:
            model_name: str = The name of the model

        Returns:
            bool: True on success, False on fail
        """
        models = self.get_models()
        button = models.get(model_name, None)
        if button is None:
            logging.error("Model %s has not found", model_name)
            logging.error("Available models are: %s", str(models.keys()))
            return False
        button.click()

        verification = button.get_attribute("aria-checked")
        if verification != "true":
            logging.error("Model switch to %s is unsuccessful", model_name)
            return False

        logging.info("Switched to %s", model_name)
        return True

    def get_plugin(self, plugin_name: str) -> Union[WebElement, None]:
        """Returns if the plugin is enabled

        Args:
            plugin_name (str): The name of the plugin

        Returns:
            bool | None : True if the plugin is enabled, False if disabled. None if not plugin doesn't exist
        """
        main_area = self.find_or_fail(
            By.TAG_NAME, self.markers.main_area_tq, return_shadow=True
        )

        side_panel = self.find_or_fail(
            By.CSS_SELECTOR,
            self.markers.side_tq,
            dom_element=main_area,
            return_shadow=True,
        )

        self.find_or_fail(
            By.CLASS_NAME, self.markers.side_buttons_cq, dom_element=side_panel, return_type="last"
        ).click()

        plugin_panel = self.find_or_fail(
            By.CSS_SELECTOR,
            self.markers.plugin_tq,
            dom_element=side_panel,
            return_shadow=True,
        )

        plugins = self.find_or_fail(
            By.CLASS_NAME,
            self.markers.p_control_cq,
            dom_element=plugin_panel,
            return_type="all",
        )

        inputs = self.find_or_fail(
            By.CSS_SELECTOR, "input", dom_element=plugin_panel, return_type="all"
        )

        plugin_map = dict(map(lambda x: (x[0].text, x[1]), zip(plugins, inputs)))

        if plugin_name not in plugin_map:
            logging.error("Plugin %s has not found", plugin_name)
            logging.error("Available plugins are: %s", str(plugin_map.keys()))
            return None

        return plugin_map[plugin_name]

    def toggle_plugin(self, plugin_name: str) -> bool:
        """Toggles the status of the plugin.
        In order to use plugins, search plugin should be active.

        Args:
            plugin_name (str): The name of the plugin

        Returns:
            bool: True if toggle action is successful, False if operation fails.
        """

        search_plugin = self.get_plugin("Search")
        if not search_plugin:
            logging.error("Unable to find search plugin")
            return False

        if not search_plugin.is_selected():
            logging.info("Search is disabled, activating it")
            search_plugin.click()
            logging.info("Search is enabled")

        p_element = self.get_plugin(plugin_name)
        if not p_element:
            logging.error("Unable to find %s plugin", plugin_name)
            return False

        logging.info(
            "The plugin is currently %s",
            ["disabled", "enabled"][p_element.is_selected()],
        )
        p_element.click()
        logging.info(
            "The plugin is now %s", ["disabled", "enabled"][p_element.is_selected()]
        )
        return True

    def regenerate_response(self):
        raise NotImplementedError("Copilot doesn't provide response regeneration")
