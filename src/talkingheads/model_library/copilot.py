"""Class definition for Copilot client"""

import time
import re
from pathlib import Path
from typing import Union, Dict

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.shadowroot import ShadowRoot
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

    def get_last_response(self, check_greeting: bool = False) -> str:
        """Returns the last response in the chat view.

        Args:
            check_greeting (bool): If set, checks the greeting message, provided after clicking New Topic.

        Returns:
            str: The last generated response
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

    def upload_image(self, action_bar: ShadowRoot, image_path: Union[str, Path]) -> bool:
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
        if url:
            camera_button = self.find_or_fail(
                By.ID,
                self.markers.cam_btn_iq,
                dom_element=action_bar
            )
            camera_button.click()
            vs = self.find_or_fail(
                By.CLASS_NAME,
                self.markers.vis_srch_cq,
                dom_element=action_bar
            )
            url_bar = self.find_or_fail(
                By.ID,
                self.markers.url_iq,
                dom_element=vs.children()[0].shadow_root
            )
            url_bar.send_keys(image_path)
            url_bar.send_keys(Keys.ENTER)
        elif file:
            im_input_element = self.find_or_fail(
                By.ID,
                self.markers.img_upload_iq,
                dom_element=action_bar,
            )
            im_input_element.send_keys(image_path)

        at_list = self.find_or_fail(
            By.CSS_SELECTOR, self.markers.at_list_cq, dom_element=action_bar, return_shadow=True
        )
        file_item = self.find_or_fail(
            By.CSS_SELECTOR, self.markers.file_item_cq, dom_element=at_list, return_shadow=True
        )
        condition = EC.presence_of_element_located((By.CLASS_NAME, self.markers.thumbnail_cq))
        WebDriverWait(file_item, 10).until(condition)
        return True

    def remove_attached_image(self) -> bool:
        """Removes the attached image from prompt

        Returns:
            bool: True if the action is valid
        """
        main_area = self.find_or_fail(
            By.TAG_NAME, self.markers.main_area_tq, return_shadow=True
        )
        action_bar = self.find_or_fail(
            By.ID, self.markers.act_bar_iq, dom_element=main_area, return_shadow=True
        )
        at_list = self.find_or_fail(
            By.CSS_SELECTOR, self.markers.at_list_cq, dom_element=action_bar, return_shadow=True
        )
        file_item = self.find_or_fail(
            By.CSS_SELECTOR, self.markers.file_item_cq, dom_element=at_list, return_shadow=True
        )
        discard_button = self.find_or_fail(
            By.CLASS_NAME,
            self.markers.dismiss_cq,
            dom_element=file_item
        )
        discard_button.click()
        return True

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
        main_area = self.find_or_fail(
            By.TAG_NAME, self.markers.main_area_tq, return_shadow=True
        )
        action_bar = self.find_or_fail(
            By.ID, self.markers.act_bar_iq, dom_element=main_area, return_shadow=True
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
            self.logger.error("Unable to locate text area, interaction fails.")
            return ""
        if image_path:
            self.upload_image(action_bar, image_path)

        for each_line in prompt.split("\n"):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)

        # Click enter and send the message
        text_area.send_keys(Keys.ENTER)

        if not self.is_ready_to_prompt(text_area, action_bar):
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
        main_area = self.find_or_fail(
            By.TAG_NAME, self.markers.main_area_tq, return_shadow=True
        )
        if not main_area:
            return False

        action_bar = self.find_or_fail(
            By.ID, self.markers.act_bar_iq, dom_element=main_area, return_shadow=True
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
            self.logger.error("Model %s has not found", model_name)
            self.logger.error("Available models are: %s", str(models.keys()))
            return False
        button.click()
        time.sleep(0.1)

        verification = button.get_attribute("aria-checked")
        if verification != "true":
            self.logger.error("Model switch to %s is unsuccessful", model_name)
            return False

        self.logger.info("Switched to %s", model_name)
        return True

    def get_plugin(self, plugin_name: str) -> Union[WebElement, None]:
        """Returns if the plugin is enabled

        Args:
            plugin_name (str): The name of the plugin

        Returns:
            Union[WebElement, None] : True if the plugin is enabled, False if disabled.
            None if not plugin doesn't exist
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

        side_button = self.find_or_fail(
            By.CLASS_NAME, self.markers.side_btns_cq, dom_element=side_panel, return_type="last"
        )
        if not side_button:
            return False

        side_button.click()

        plugin_panel = self.find_or_fail(
            By.CSS_SELECTOR,
            self.markers.plugin_tq,
            dom_element=side_panel,
            return_shadow=True,
        )
        time.sleep(0.5)
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
            self.logger.error("Plugin %s has not found", plugin_name)
            self.logger.error("Available plugins are: %s", str(plugin_map.keys()))
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
            self.logger.error("Unable to find search plugin")
            return False

        if not search_plugin.is_selected():
            self.logger.info("Search is disabled, activating it")
            search_plugin.click()
            self.logger.info("Search is enabled")

        p_element = self.get_plugin(plugin_name)
        if not p_element:
            self.logger.error("Unable to find %s plugin", plugin_name)
            return False

        self.logger.info(
            "The plugin is currently %s",
            ["disabled", "enabled"][p_element.is_selected()],
        )
        p_element.click()
        time.sleep(0.5)
        self.logger.info(
            "The plugin is now %s", ["disabled", "enabled"][p_element.is_selected()]
        )
        return True

    def regenerate_response(self):
        raise NotImplementedError("Copilot doesn't provide response regeneration")
