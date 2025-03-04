"""
This module provides a base class `BaseBrowser` for automating web interactions using the 
`undetected_chromedriver` package and Selenium WebDriver.

The `BaseBrowser` class establishes core for different chatbot interfaces, providing common 
features such as headless mode, incognito browsing, login functionality, and interaction with 
web elements. It also includes utility functions for handling timeouts, saving chat history, 
and performing custom pre- and post-load actions on webpages.

Key Features:
    - Browser automation using undetected_chromedriver and Selenium.
    - Configurable headless, incognito modes, and driver arguments.
    - Timeout management for page load and element interactions.
    - Automatic login and credential management using environment variables.
    - Logging and verbose mode for detailed tracking of actions.
    - Functions to find, wait for, and interact with web elements.
    - Chat history saving and automatic response logging.

The module also includes abstract methods (`login`, `interact`, `reset_thread`, etc.) 
that should be implemented by subclasses for specific automation workflows, like interacting 
with a chatbot or performing other automated web tasks.
"""

import asyncio
import abc
import os
import logging
import re
import time
from datetime import datetime
from typing import Union, Optional
from pathlib import Path

import pandas as pd

import nodriver as nd

from .object_map import markers
from .utils import save_func_map


class BaseBrowser:
    """
    A base class for browser automation that includes login, interaction, and session management
    for various clients. This class provides essential browser functionality like loading web pages,
    managing timeouts, saving chat logs, and handling login processes, which can be customized
    for different clients.

    Args:
        client_name (str): Name of the client.
        url (str): URL to be used as the starting point of the session.
        uname_var (str): Environment variable name for the username.
        pwd_var (str): Environment variable name for the password.
        username (str, optional): Username (deprecated, environment variables recommended).
        password (str, optional): Password (deprecated, environment variables recommended).
        headless (bool, optional): Enables/disables headless mode. Default: True.
        cold_start (bool, optional): If True, load the page and return. Default: False.
        incognito (bool, optional): Enables incognito mode if True. Default: True.
        driver_arguments (list, optional): Additional arguments for the browser driver.
        driver_version (int, optional): Version of the ChromeDriver to use.
        auto_save (bool, optional): A boolean to enable/disable automatic saving. Default: False.
        save_path (str, optional): Path to save chat logs.
        verbose (bool, optional): A boolean to enable/disable logging. Default: False.
        credential_check (bool, optional): Enables/disables credential check. Default: True.
        skip_login (bool, optional): If True, skips the login procedure. Default: False.
        user_data_dir (str, optional): The directory path to user profile.
        uc_params (dict, optional): Additional parameters for undetected Chrome (uc.Chrome).
            Some examples : driver_executable_path, browser_executable_path

    Attributes:
        client_name (str): Client name provided during initialization.
        browser (uc.Chrome): The undetected Chrome browser instance.
        markers (dict): Markers used for locating elements on the page.
        logger (logging.Logger): Logger for the browser class.
        ready (bool): Whether the browser is fully initialized and ready.
        timeout_dur (int): Page load and element wait timeout duration.
        chat_history (pd.DataFrame): DataFrame that holds chat history.
    """

    def __init__(
        self,
        client_name: str,
        url: str,
        uname_var: Union[str, None] = None,
        pwd_var: Union[str, None] = None,
        headless: bool = True,
        save_path: Union[str, bool] = None,
        verbose: bool = False,
        credential_check: bool = True,
        skip_login: bool = False,
        user_data_dir: str = None,
        browser_arguments: list = None,
        tag: str = None,
        multihead: bool = False,
        debug: bool = True
    ):
        self.client_name = client_name
        self.markers = markers[client_name]
        self.url = url
        self.uname_var = uname_var or f"{client_name}_UNAME"
        self.pwd_var = pwd_var or f"{client_name}_PWD"
        self.headless = headless
        self.browser = None
        self.last_prompt = ""
        self.tag = tag or self.client_name
        self.multihead = multihead
        self.interim_response = None
        self.user_data_dir = user_data_dir or ""
        self.browser_arguments = browser_arguments or []
        self.skip_login = skip_login
        self.tab = None
        self.ready = False
        self.debug = debug

        if not skip_login and credential_check:
            if not os.environ.get(self.uname_var):
                raise NameError(f"Set the environment variable {self.uname_var}")
            if not os.environ.get(self.pwd_var):
                raise NameError(f"Set the environment variable {self.pwd_var}")

        # Get currenty logging level
        r_level = logging.getLogger().getEffectiveLevel()
        # Set new logger
        self.logger = logging.getLogger(self.tag)
        self.logger.setLevel(r_level)

        # If verbose is provided and the current log level is higher
        # than info, it will decrease logging level.
        if verbose and not self.logger.isEnabledFor(logging.INFO):
            self.logger.setLevel(logging.INFO)
            self.logger.info("Verbose mode active")

        self.logger.info("%s is ready to interact", self.client_name)
        self.ready = True
        self.chat_history = pd.DataFrame(columns=["role", "is_regen", "content"])
        self.set_save_path(save_path)

    async def start(self):
        """_summary_

        Raises:
            RuntimeError: _description_
        """
        self.logger.info("Loading nodriver")
        self.browser = await nd.start(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            browser_args=self.browser_arguments
        )

        self.logger.info("Loaded nodriver")
        self.logger.info("Opening %s", self.client_name)

        await self.preload_custom_func()
        self.tab = await self.browser.get(self.url)
        await self.postload_custom_func()

        if not await self.pass_verification():
            raise RuntimeError("Verification failed, please check your connection.")

        if not self.skip_login:
            await self.login()

        self.logger.info("%s is ready to interact", self.client_name)
        self.ready = True

    def __del__(self):
        if getattr(self, "browser", None) and not self.browser.stopped:
            self.browser.stop()

        if getattr(self, "save_path", None):
            self.save()


    def set_save_path(self, save_path: Union[str, bool]):
        """
        Sets the file path to save the chat log. If a boolean value is provided,
        a timestamped file with the default extension 'csv' is created in the current
        working directory.

        Args:
            save_path (Union[str, bool]): The save path for the chat log. If True,
            a timestamped file name with the 'csv' extension is generated.
        """
        if isinstance(save_path, bool):
            self.save_path = datetime.now().strftime(
                f"{self.tag}_%Y_%m_%d_%H_%M_%S.csv"
            )
        else:
            self.save_path = save_path

        self.file_type = save_path.split(".")[-1]

    def save(self) -> bool:
        """
        Saves the chat history to a file using the provided save path and file format.

        Returns:
            bool: True if the file was successfully saved, False otherwise.
        """
        save_func = save_func_map.get(self.file_type, None)
        if save_func is None:
            self.logger.error("Unsupported file type %s", self.file_type)
            return False

        save_func = getattr(self.chat_history, save_func)
        if save_func is None:
            logging.error("No such save function")
            return False

        save_func(self.save_path)
        self.logger.info("File saved to %s", self.save_path)
        return True

    async def find_or_fail(
        self, xpath: str, return_type: str = "first", fail_ok: bool = False
    ):
        """
        Finds elements based on the provided query and locator method.
        Raises an error if no element is found and fail_ok is False.

        Args:
            by (By): The method used to locate the element (e.g., By.ID, By.XPATH).
            elem_query (str): The query string for locating the element.
            return_type (str): What to return ('first', 'all', or 'last'). Default is 'first'.
            fail_ok (bool): o not produce error if it is ok to fail.
            dom_element (WebElement): If set, finds within that element.
        Returns:
            WebElement: The found web element or None if not found.
        """

        return_types = {
            "first": lambda x: x[0],
            "all": lambda x: x,
            "last": lambda x: x[-1],
        }

        return_fn = return_types.get(return_type)

        if return_fn is None:
            return ValueError("Unrecognized return type")

        dom_elements = await self.tab.find_elements_by_text(xpath)

        if not dom_elements:
            log_fn = self.logger.info if fail_ok else self.logger.error
            log_fn(" %s is not located.", xpath)
            if not fail_ok and self.debug:
                await self.save_screenshot(xpath)
            return None

        self.logger.info(" %s is located.", xpath)

        dom_element = return_fn(dom_elements)
        return dom_element

    async def is_login_page(self):
        """
        Checks whether the login page is currently displayed.

        Returns:
            bool: True if the login button is not present, False otherwise.
        """
        login_button = await self.tab.find_elements_by_text(self.markers.login)
        return len(login_button) == 1

    async def wait_until_appear(self, xpath: str, timeout: int = 10, fail_ok=False):
        """
        Waits until the specified web element appears on the page.

        This function continuously checks for the presence of a web element.
        It waits until the element is present on the page.
        Once the element has appeared, the function returns.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            elem_query (str): The elem_query string to locate the element.
            timeout (int, optional): Waiting time before the timeout. Default: 10
            fail_ok (bool, optional): If True, skips logging error if element is absent.

        Returns:
            WebElement | None: The web element if found, otherwise None.
        """
        self.logger.info("Waiting element %s to appear.", xpath)
        element = None
        try:
            for _ in range(timeout):
                element = await self.find_or_fail(xpath, fail_ok=True)
                if element:
                    self.logger.info("Element %s appeared.", xpath)
                    break
                await asyncio.sleep(1)
        except TimeoutError:
            if not fail_ok:
                self.logger.error(
                    "Element %s is not present, something is wrong.", xpath
                )
                if self.debug:
                    await self.save_screenshot(xpath)
        return element

    async def wait_until_disappear(
        self, xpath: str, timeout: int = 10, wait_per_step: int = 0.2
    ) -> bool:
        """
        Waits until the specified web element disappears from the page.

        This function continuously checks for the presence of a web element.
        It waits until the element is no longer present on the page.
        Once the element has disappeared, the function returns.

        Args:
            xpath (str): The xpath string to locate the element.
            timeout (int, optional): Waiting time before the timeout. Default: 10.

        Returns:
            (bool) : True if element disappears, false otherwise.
        """

        start = time.time()
        current = time.time()
        while current - start < timeout:
            item = await self.find_or_fail(xpath, fail_ok=True)
            if not item:
                self.logger.info("The item %s has disappeared", xpath)
                return True
            self.logger.debug("The item is still present, waiting")
            time.sleep(max(0, wait_per_step - (time.time() - current)))
            current = time.time()

        self.logger.error("Item is still present")
        return False

    def log_chat(
        self, prompt: str = None, response: str = None, regenerated: bool = False
    ) -> bool:
        """
        Log a chat interaction in the chat history.

        Args:
            prompt (str): The user's prompt to be logged.
            response (str): The response to the user's prompt to be logged.

        Returns:
            bool: True if the interaction is logged, False otherwise.
        """
        if not self.save_path:
            return False

        if prompt:
            self.chat_history.loc[len(self.chat_history)] = [
                "user",
                regenerated,
                prompt,
            ]

        if response:
            self.chat_history.loc[len(self.chat_history)] = [
                self.client_name,
                regenerated,
                response,
            ]
        return True

    async def preload_custom_func(self) -> None:
        """
        A function to implement custom instructions before loading the webpage
        """
        self.logger.debug("No custom preload function is implemented")

    async def postload_custom_func(self) -> None:
        """
        A function to implement custom instructions after loading the webpage
        """
        self.logger.debug("No custom postload function is implemented")

    async def pass_verification(self) -> bool:
        """
        Performs the verification process on the page if challenge is present.
        Returns:
            None
        """
        self.logger.info("The pass verification function is not implemented")
        return True

    @abc.abstractmethod
    async def login(self) -> bool:
        """
        Performs the login process with the provided username and password.
        """
        self.logger.warning(
            "If you are creating a custom automation, please implement this method!"
        )

    async def get_last_response(
        self, num_step: int = 200, period: float = 0.5, same_answer_limit=3
    ) -> str:
        """
        Continuously checks for a response in a chatbox-like element and
            returns the last received response.

        Args:
            num_step (int): Number of cycles to check for updates to the response.
                Defaults to 200.
            period (float): Sleep time between each step, representing the delay between each check.
                Defaults to 0.5 seconds.
            same_answer_limit (int): The maximum number of times the same response can
                be observed before concluding that the response is complete. Defaults to 3.

        Returns:
            str: The last valid response from the chatbox element.
                If no response is found, an empty string is returned.

        Behavior:
            - The function first waits for the chatbox element to appear on the page.
            - It continuously checks for updates to the response in the chatbox.
            - The response is checked continuously, `period` seconds between each check.
            - If the response remains the same for more than `same_answer_limit` consecutive times,
                the loop breaks, assuming the response is complete.
            - If no response is found, it returns an empty string.
            - If a response is found, it returns the last detected response.
        """

        self.logger.info("Checking the response")

        self.interim_response = None
        await self.wait_until_appear(self.markers.chatbox)

        same_answer = 0
        for _ in range(num_step):
            time.sleep(period)
            l_response = await self.response_parser()
            same_answer = [0, same_answer + 1][l_response == self.interim_response]

            self.interim_response = l_response
            if same_answer > same_answer_limit:
                break

        if not self.interim_response:
            self.logger.error("There is no response, something is wrong")
            return ""

        self.logger.info("response is ready")
        return self.interim_response

    async def interact(self, prompt: str, image_path: Union[str, Path] = None) -> str:
        """Sends a prompt and retrieves the response from the user interface.

        This function interacts with the user interface.
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
        if image_path:
            uploaded = await self.upload_file(image_path)
            if not uploaded:
                self.logger.error("Image is not uploaded.")
                return ""

        text_area = await self.wait_until_appear(self.markers.textarea)
        if not text_area:
            raise RuntimeError(
                "Unable to find the text prompt area. Please raise an issue with verbose=True"
            )

        prompt = prompt.replace("\n", "\r\n")
        await text_area.focus()
        await self.tab.send(nd.cdp.input_.insert_text(text=prompt))
        await self.tab.send(nd.cdp.input_.insert_text(text='\n'))

        send_button = await self.find_or_fail(self.markers.send)
        await send_button.click()

        response = await self.get_last_response()

        self.log_chat(prompt=prompt, response=response)
        return response

    async def response_parser(self) -> Optional[str]:
        """
        Abstract function to open a new thread.
        """
        response_element = await self.find_or_fail(self.markers.chatbox, return_type="last")
        if response_element:
            return response_element.text_all
        self.logger.warning("Response is not available.")
        return None
    
    async def save_screenshot(self, xpath):
        xpath = re.sub(r"/+", "_", xpath)
        await self.tab.save_screenshot(f"{self.client_name}_{xpath}_{time.time()}.png")

    @staticmethod
    async def clear_input(element):
        await element.apply('function (element) { element.select() } ')
        return await element.tab.send(nd.cdp.input_.insert_text(''))

    @abc.abstractmethod
    async def upload_file(self, file_path: Union[str, Path]) -> bool:
        """
        Abstract function to open a new thread.
        """
        self.logger.warning("File upload is either not implemented or not available")

    @abc.abstractmethod
    async def reset_thread(self) -> bool:
        """
        Abstract function to open a new thread.
        """
        self.logger.warning(
            "Resetting thread is either not implemented or not available"
        )

    @abc.abstractmethod
    async def regenerate_response(self) -> str:
        """
        Abstract function to regenerate the responses.
        """
        self.logger.warning(
            "Regenerating response is either not implemented or not available"
        )

    @abc.abstractmethod
    async def switch_model(self, model_name: str) -> bool:
        """
        Abstract function to switch the model.

        Args:
            model_name: (str) = The name of the model.
        """
        self.logger.warning(
            "Switching model is either not implemented or not available"
        )
