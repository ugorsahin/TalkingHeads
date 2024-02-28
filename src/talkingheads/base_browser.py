"""Class definition for ChatGPT_Client"""

import abc
import os
import logging
from datetime import datetime
from typing import Union

import undetected_chromedriver as uc
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import selenium.common.exceptions as Exceptions

from .object_map import markers
from .utils import detect_chrome_version, save_func_map


class BaseBrowser:
    """
    BaseBrowser class to provide utility function and flow for LLMs

    Args:
        client_name (str): A string representing the name of the client.
        url (str): The URL to be used as an entrypoint.
        uname_var (str): The username environment variable, to enable multiple agents.
        pwd_var (str): The password environment variable, to enable multiple agents.
        username (str, optional): Deprecated. Use environment variables instead.
        password (str, optional): Deprecated. Use environment variables instead.
        headless (bool, optional): Enables/disables headless mode. Default: True.
        cold_start (bool, optional): If set, it will return after opening the browser. Default: False.
        incognito (bool, optional): A boolean to set incognito mode. Default: True.
        driver_arguments (list, optional): A list of additional arguments to be passed to the driver. Default: None.
        driver_version (int, optional): The version of the chromedriver. Default: None.
        auto_save (bool, optional): A boolean to enable/disable automatic saving. Default: False.
        save_path (str, optional): The file path to save chat logs. Default: None.
        verbose (bool, optional): A boolean to enable/disable logging. Default: False.
        credential_check (bool, optional): Enables/disables credential check. Default: True.
        skip_login (bool, optional): If True, skips the login procedure. Default: False.
        user_data_dir (str, optional): The directory path to user profile. Default: None.
        uc_params (dict, optional): Parameters for uc.Chrome().
            Some examples : driver_executable_path, browser_executable_path

    Returns:
        BaseBrowser: The base driver object.
    """

    def __init__(
        self,
        client_name: str,
        url: str,
        uname_var: Union[str, None] = None,
        pwd_var: Union[str, None] = None,
        username: Union[str, None] = None,
        password: Union[str, None] = None,
        headless: bool = True,
        cold_start: bool = False,
        incognito: bool = True,
        driver_arguments: list = None,
        driver_version: int = None,
        timeout_dur: int = 15,
        auto_save: bool = False,
        save_path: str = None,
        verbose: bool = False,
        credential_check: bool = True,
        skip_login: bool = False,
        user_data_dir: str = None,
        uc_params: dict = None,
    ):
        self.client_name = client_name
        self.markers = markers[client_name]
        self.url = url
        self.uname_var = uname_var or f"{client_name}_UNAME"
        self.pwd_var = pwd_var or f"{client_name}_PWD"
        self.headless = headless
        self.ready = False
        self.auto_save = auto_save

        if credential_check:
            if username or password:
                logging.warning(
                    "The username and password parameters are deprecated and will be removed soon."
                    " Please adjust your environment variables to pass username and password."
                )

            username = username or os.environ.get(self.uname_var)
            password = password or os.environ.get(self.pwd_var)

            if not username:
                raise NameError(
                    f"Either provide username or set the environment variable {self.uname_var}"
                )

            if not password:
                raise NameError(
                    f"Either provide password or set the environment variable {self.pwd_var}"
                )

        if verbose:
            logging.getLogger().setLevel(logging.INFO)
            logging.info("Verbose mode active")
        options = uc.ChromeOptions()
        options.headless = self.headless
        if incognito:
            options.add_argument("--incognito")
        if driver_arguments:
            for _arg in driver_arguments:
                options.add_argument(_arg)

        logging.info("Loading undetected Chrome")
        uc_params = uc_params or {}
        self.browser = uc.Chrome(
            user_data_dir=user_data_dir,
            options=options,
            headless=headless,
            version_main=detect_chrome_version(driver_version),
            **uc_params,
        )
        self.wait_object = WebDriverWait(self.browser, timeout_dur)
        agent = self.browser.execute_script("return navigator.userAgent")
        self.browser.execute_cdp_cmd(
            "Network.setUserAgentOverride", {"userAgent": agent.replace("Headless", "")}
        )
        self.browser.set_page_load_timeout(15)

        logging.info("Loaded undetected Chrome")
        logging.info("Opening %s", self.client_name)

        self.preload_custom_func()
        self.browser.get(self.url)
        if cold_start:
            return

        self.postload_custom_func()
        if not self.pass_verification():
            raise RuntimeError("Verification failed, please check your connection.")

        if not skip_login:
            self.login(username, password)

        logging.info("%s is ready to interact", self.client_name)
        self.ready = True
        self.chat_history = pd.DataFrame(columns=["role", "is_regen", "content"])
        self.set_save_path(save_path)

    def __del__(self):
        self.browser.close()
        self.browser.quit()
        if self.auto_save:
            self.save()

    def set_save_path(self, save_path: str):
        """Sets the path to save the file

        Args:
            save_path (str): The saving path
        """
        self.save_path = save_path or datetime.now().strftime("%Y_%m_%d_%H_%M_%S.csv")
        self.file_type = save_path.split(".")[-1] if save_path else "csv"

    def save(self) -> bool:
        """Saves the conversation."""
        save_func = save_func_map.get(self.file_type, None)
        if save_func:
            save_func = getattr(self.chat_history, save_func)
            save_func(self.save_path)
            logging.info("File saved to %s", self.save_path)
            return True

        logging.error("Unsupported file type %s", self.file_type)
        return False

    def find_or_fail(
        self,
        by: By,
        elem_query: str,
        return_type: str = "first",
        return_shadow: bool = False,
        fail_ok: bool = False,
        dom_element: WebElement = None,
    ):
        """Finds a list of elements given elem_query, if none of the items exists, throws an error

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            elem_query (str): The elem_query string to locate the element.
            return_type (str): first|all|last. Return first element, all elements or the last one.
            fail_ok (bool): Do not produce error if it is ok to fail.
            dom_element (WebElement): If set, finds within that element.
        Returns:
            WebElement: Web element or None if not found.
        """

        if return_type not in {"first", "last", "all"}:
            return ValueError("Unrecognized return type")

        if dom_element is None:
            dom_element = self.browser.find_elements(by, elem_query)
        else:
            dom_element = dom_element.find_elements(by, elem_query)

        if not dom_element:
            if not fail_ok:
                logging.error(
                    "%s is not located. Please raise an issue with verbose=True", elem_query
                )
            else:
                logging.info("%s is not located.", elem_query)
            return None

        logging.info("%s is located.", elem_query)

        element = {
            "first": lambda x: x[0],
            "all": lambda x: x,
            "last": lambda x: x[-1],
        }[return_type](dom_element)

        if return_shadow:
            return element.shadow_root
        return element

    def check_login_page(self):
        """
        Checks if the login page is displayed in the browser.

        Returns:
            bool: True if the login page is not present, False otherwise.
        """
        login_button = self.browser.find_elements(By.XPATH, self.markers.login_xq)
        return len(login_button) == 0

    def wait_until_appear(self, by: By, elem_query: str) -> Union[WebElement, None]:
        """
        Waits until the specified web element appears on the page.

        This function continuously checks for the presence of a web element.
        It waits until the element is present on the page.
        Once the element has appeared, the function returns.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            elem_query (str): The elem_query string to locate the element.
            timeout_dur (int, optional): Waiting time before the timeout. Default: 15.

        Returns:
            (WebElement | None): If element is appeared, it returns the element. Otherwise,
            it returns None.
        """
        logging.info("Waiting element %s to appear.", elem_query)
        element = None
        try:
            element = self.wait_object.until(
                EC.presence_of_element_located((by, elem_query))
            )
            logging.info("Element %s appeared.", elem_query)
        except Exceptions.TimeoutException:
            logging.info("Element %s is not present, something is wrong.", elem_query)
        return element

    def wait_until_disappear(self, by: By, elem_query: str) -> bool:
        """
        Waits until the specified web element disappears from the page.

        This function continuously checks for the presence of a web element.
        It waits until the element is no longer present on the page.
        Once the element has disappeared, the function returns.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            elem_query (str): The elem_query string to locate the element.
            timeout_dur (int, optional): Waiting time before the timeout. Default: 15.

        Returns:
            (bool) : True if element disappears, false otherwise.
        """
        logging.info("Waiting element %s to disappear.", elem_query)
        try:
            self.wait_object.until_not(EC.presence_of_element_located((by, elem_query)))
            logging.info("Element %s disappeared.", elem_query)
            return True
        except Exceptions.TimeoutException:
            logging.info("Element %s still here, something is wrong.", elem_query)
            return False

    def log_chat(
        self, prompt: str = None, answer: str = None, regenerated: bool = False
    ) -> bool:
        """
        Log a chat interaction in the chat history.

        Parameters:
        - prompt (str): The user's prompt to be logged.
        - answer (str): The answer to the user's prompt to be logged.

        Returns:
        - bool: True if the interaction is logged, False otherwise.
        """
        if not self.auto_save:
            return False

        if prompt:
            self.chat_history.loc[len(self.chat_history)] = [
                "user",
                regenerated,
                prompt,
            ]
        if answer:
            self.chat_history.loc[len(self.chat_history)] = [
                self.client_name,
                regenerated,
                answer,
            ]
        return True

    def preload_custom_func(self) -> None:
        """
        A function to implement custom instructions before loading the webpage
        """
        logging.info("The preload behavior is not implemented")

    def postload_custom_func(self) -> None:
        """
        A function to implement custom instructions after loading the webpage
        """
        logging.info("The postload behavior is not implemented")

    def pass_verification(self) -> bool:
        """
        Performs the verification process on the page if challenge is present.
        Returns:
            None
        """
        logging.info("The pass verification function is not implemented")
        return True

    @abc.abstractmethod
    def login(self, username: str, password: str) -> bool:
        """
        Performs the login process with the provided username and password.
        """
        logging.warning(
            "If you are creating a custom automation, please implement this method!"
        )

    @abc.abstractmethod
    def interact(self, prompt: str) -> str:
        """
        Abstract function to interact with the language model.
        """
        logging.warning(
            "If you are creating a custom automation, please implement this method!"
        )

    @abc.abstractmethod
    def reset_thread(self) -> bool:
        """
        Abstract function to open a new thread.
        """
        logging.warning("Resetting thread is either not implemented or not available")

    @abc.abstractmethod
    def regenerate_response(self) -> str:
        """
        Abstract function to regenerate the answers.
        """
        logging.warning(
            "Regenerating response is either not implemented or not available"
        )

    @abc.abstractmethod
    def switch_model(self, model_name: str) -> bool:
        """
        Abstract function to switch the model.

        Args:
            model_name: (str) = The name of the model.
        """
        logging.warning("Switching model is either not implemented or not available")
