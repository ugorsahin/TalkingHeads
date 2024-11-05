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
