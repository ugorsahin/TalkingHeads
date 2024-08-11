"""Class definition for GeminiClient"""

import time
from typing import Union
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

    def login(self, username: str, password: str) -> bool:
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
        text_area = self.wait_until_appear(By.XPATH, self.markers.textarea_xq)
        if not text_area and not self.headless:
            for _ in range(5):
                self.logger.error(
                    """Prompt area can\'t located, use browser to manually
                    login your account, navigate to %s
                    and press any key here.""", self.url
                )
                input()
                text_area = self.find_or_fail(By.XPATH, self.markers.textarea_xq)
                break
            else:
                self.logger.error("Login is unsuccesful")
                return False
        return True


    def postload_custom_func(self):
        self.browser.get(self.url)

    def get_response(self, tick_step: int = 40, tick_period : float = 0.5, max_same_ans : int = 3) -> str:
        """Get the response from chat board

        Returns:
            str: The interaction text
        """
        self.logger.info("Message sent, waiting for response")
        self.interim_response = None
        self.wait_until_appear(By.TAG_NAME, self.markers.chatbox_tq)
        counter = 0
        for _ in range(tick_step):
            time.sleep(tick_period)
            l_response = self.find_or_fail(
                By.TAG_NAME, self.markers.chatbox_tq, return_type="last"
            ).text
            if l_response and l_response == self.interim_response:
                counter += 1
            if counter > max_same_ans:
                break
            self.interim_response = l_response

        if not self.interim_response:
            self.logger.error("There is no response, something is wrong")
            return ""

        self.logger.info("response is ready")
        return self.interim_response

        # return response.text


    def upload_image(self, image_path: Union[str, Path]) -> bool:
        """Upload an image or a url and wait until it is uploaded,
        then returns.

        Args:
            image_path (Union[str, Path]): the file path to image or the url.

        Returns:
            bool: True if the image loaded properly, False otherwise.
        """
        if isinstance(image_path, Path):
            image_path = str(image_path)
        if not check_filetype(image_path, self.markers.file_types):
            self.logger.error(
                "File type should be one of the following: %s",
                ", ".join(self.markers.file_types)
            )
            return False

        im_input_element = self.find_or_fail(By.XPATH, self.markers.img_upload_xq, fail_ok=True)
        if not im_input_element:
            # Input element only appears when we click the image button
            # However, clicking this button will open file upload dialog,
            # and driver can't close that dialog. As a workaround,
            # we disable the click event on input element and then click the
            # button, so that we avoid opening the dialog but the
            # input element is safely loaded.
            self.browser.execute_script("HTMLInputElement.prototype.click = function(){}")
            im_button = self.find_or_fail(By.XPATH, self.markers.img_btn_xq)
            if not im_button:
                return False
            im_button.click()

            # Check if there is a modal, click True if there is
            got_it_button = self.find_or_fail(By.XPATH, self.markers.got_it_xq, fail_ok=True)
            if got_it_button:
                got_it_button.click()
                time.sleep(0.3)
                im_button.click()

            im_input_element = self.wait_until_appear(By.XPATH, self.markers.img_upload_xq)
            if not im_input_element:
                return False

        im_input_element.send_keys(image_path)
        uploaded = self.wait_until_appear(By.XPATH, self.markers.img_loaded_xq)
        if not uploaded:
            self.logger.error('Image upload failed.')
            return False

        self.logger.info('Image uploaded.')
        return True

    def interact(self, prompt: str, image_path: Union[str, Path] = None) -> str:
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
            uploaded = self.upload_image(image_path)
            if not uploaded:
                return ""

        text_area = self.find_or_fail(By.XPATH, self.markers.textarea_xq)
        if not text_area:
            return ""
        for each_line in prompt.split("\n"):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)

        response = self.get_response()
        if not response:
            return ""
        self.last_prompt = prompt
        self.log_chat(prompt=prompt, response=response)
        return response

    def reset_thread(self) -> bool:
        """Function to close the current thread and start new one

        Returns:
            bool: True new chat button is clicked, false otherwise
        """
        new_chat_button = self.find_or_fail(By.XPATH, self.markers.new_chat_xq)
        if not new_chat_button:
            return False
        new_chat_button.click()


        dialog_confirm = self.find_or_fail(By.XPATH, self.markers.chat_conf_xq, fail_ok=True)
        if dialog_confirm:
            dialog_confirm.click()
            self.logger.info('Confirmed New Chat in dialog window')

        time.sleep(0.5)
        responses = self.browser.find_elements(By.TAG_NAME, self.markers.chatbox_tq)
        if len(responses) > 0:
            self.logger.error("Couldn\'t reset the chat")
            return False

        self.logger.info("New chat is ready")
        return True

    def regenerate_response(self) -> str:
        """Closes the current thread and starts a new one.

        Args:
            None

        Returns:
            str: The regenerated response or empty string in case of failure.
        """
        draft_button = self.find_or_fail(By.XPATH, self.markers.regen_1_xq)
        if not draft_button:
            return ""
        draft_button.click()
        self.logger.info("Clicked drafts button")

        self.wait_object.until(
            EC.element_to_be_clickable((By.CLASS_NAME, self.markers.regen_2_cq))
        ).click()
        self.logger.info("Clicked regenerate button")

        response = self.get_response()
        self.logger.info("New response is ready")

        self.log_chat(response=response, regenerated=True)
        return response

    def modify_response(self, mode: str) -> str:
        """Closes the current thread and starts a new one.

        Args:
            mode: Select the modification mode.

        Returns:
            str: The regenerated response or empty string in case of failure.
        """
        modify_button = self.find_or_fail(By.XPATH, self.markers.modify_xq)
        if not modify_button:
            return ""
        modify_button.click()
        self.logger.info("Clicked Modify response button")

        options = self.find_or_fail(By.XPATH, self.markers.mod_opt_xq, return_type='all')
        if not options:
            return ""

        options = dict(map(
            lambda x: ((x.text.split('\n')[-1].lower()), x),
            options
        ))

        selected_option = options.get(mode)
        if not selected_option:
            self.logger.error(
                'The provided mode doesn\'t exist, select from the following: %s',
                ', '.join(options)
            )
            list(options.values())[0].send_keys(Keys.ESCAPE)
            return ""
        selected_option.click()

        response = self.get_response()
        self.log_chat(response=response, regenerated=True)
        return response

    def switch_model(self, model_name: str) -> bool:
        self.logger.info("Gemini doesn't have a model selection")
        return False
