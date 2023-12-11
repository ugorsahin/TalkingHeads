'''Class definition for ChatGPT_Client'''

import abc
import os
import logging
import time
from datetime import datetime

import undetected_chromedriver as uc
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as Exceptions

from .object_map import markers
from .utils import detect_chrome_version, save_func_map

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.WARNING
)

class BaseBrowser:
    '''
    BaseBrowser class to provide utility function and flow for LLMs

    Args:
        client_name (str): A string representing the name of the client.
        url (str): The URL to be used as an entrypoint.
        uname_env_var (str): The username variable set by llm classes.
        pwd_env_var (str): The password variable set by llm classes.
        username (str, optional): The username to auth. Deprecated. Use environment variables instead.
        password (str, optional): The password to auth. Deprecated. Use environment variables instead.
        headless (bool, optional): A boolean to enable/disable headless mode in driver. Default: True.
        cold_start (bool, optional): If set, it will return after opening the browser. Default: False.
        incognito (bool, optional): A boolean to set incognito mode. Default: True.
        driver_arguments (list, optional): A list of additional arguments to be passed to the driver. Default: None.
        driver_version (int, optional): The version of the chromedriver. Default: None.
        auto_save (bool, optional): A boolean to enable/disable automatic saving. Default: False.
        save_path (str, optional): The file path to save chat logs. Default: None.
        verbose (bool, optional): A boolean to enable/disable logging. Default: False.
        credential_check (bool, optional): A boolean to enable/disable credential check. Default: True.
        skip_login (bool, optional): If True, skips the login procedure. Default: False.
        user_data_dir (str, optional): The directory path to user profile. Default: None.
        uc_params (dict, optional): Parameters for uc.Chrome().
            Some examples : driver_executable_path, browser_executable_path

    Returns:
        BaseBrowser: The base driver object. 
    '''

    def __init__(
        self,
        client_name : str,
        url : str,
        uname_env_var : str,
        pwd_env_var : str,
        username: str = '',
        password: str = '',
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
        uc_params : dict = None,
    ):
        self.client_name    = client_name
        self.markers        = markers[client_name]
        self.url            = url
        self.uname_env_var  = uname_env_var
        self.pwd_env_var    = pwd_env_var
        self.headless       = headless
        self.ready          = False
        self.auto_save = auto_save

        if credential_check:
            if username or password:
                logging.warning(
                    "The username and password parameters are deprecated and will be removed soon."
                    " Please adjust your environment variables to pass username and password."
                )

            username = username or os.environ.get(self.uname_env_var)
            password = password or os.environ.get(self.pwd_env_var)

            if not username:
                raise NameError(
                    f'Either provide username or set the environment variable {self.uname_env_var}')

            if not password:
                raise NameError(
                    f'Either provide password or set the environment variable {self.pwd_env_var}')

        if verbose:
            logging.getLogger().setLevel(logging.INFO)
            logging.info('Verbose mode active')
        options = uc.ChromeOptions()
        options.headless = self.headless
        if incognito:
            options.add_argument('--incognito')
        if driver_arguments:
            for _arg in driver_arguments:
                options.add_argument(_arg)

        logging.info('Loading undetected Chrome')
        uc_params = uc_params or {}
        self.browser = uc.Chrome(
            user_data_dir=user_data_dir,
            options=options,
            headless=headless,
            version_main=detect_chrome_version(driver_version),
            **uc_params
        )
        self.wait_object = WebDriverWait(self.browser, timeout_dur)
        agent = self.browser.execute_script("return navigator.userAgent")
        self.browser.execute_cdp_cmd(
            'Network.setUserAgentOverride',
            {"userAgent": agent.replace('Headless', '')}
        )
        self.browser.set_page_load_timeout(15)
        if cold_start:
            return

        logging.info('Loaded undetected Chrome')
        logging.info('Opening %s', self.client_name)

        self.preload_custom_func()
        self.browser.get(self.url)
        self.postload_custom_func()
        if not self.pass_verification():
            raise RuntimeError('Verification failed, please check your connection.')

        if not skip_login:
            self.login(username, password)

        logging.info('%s is ready to interact', self.client_name)
        self.ready = True
        self.chat_history = pd.DataFrame(columns=['role', 'is_regen', 'content'])
        self.set_save_path(save_path)

    def __del__(self):
        self.browser.quit()
        if self.auto_save:
            self.save()

    def set_save_path(self, save_path : str):
        """Sets the path to save the file

        Args:
            save_path (str): The saving path
        """
        self.save_path = save_path or datetime.now().strftime('%Y_%m_%d_%H_%M_%S.csv')
        self.file_type = save_path.split('.')[-1] if save_path else 'csv'

    def save(self) -> bool:
        """Saves the conversation."""
        save_func = save_func_map.get(self.file_type, None)
        if save_func:
            save_func = getattr(self.chat_history, save_func)
            save_func(self.save_path)
            logging.info('File saved to %s', self.save_path)
            return True

        logging.error('Unsupported file type %s', self.file_type)
        return False

    def find_or_fail(self, by: By, query: str, return_type: str = 'first', fail_ok: bool = False):
        """Finds a list of elements given query, if none of the items exists, throws an error

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            query (str): The query string to locate the element.
            return_type (str): First|all|last. Return first element, all elements or the last one.
            fail_ok (bool): Do not produce error if it is ok to fail.
        Returns:
            selenium.webdriver.remote.webelement.WebElement: Web element or None if not found.
        """
        dom_element = self.browser.find_elements(by, query)
        if not dom_element:
            if not fail_ok:
                logging.error('%s is not located. Please raise an issue with verbose=True', query)
            else:
                logging.info('%s is not located.', query)
            return None

        logging.info('%s is located.', query)

        if return_type == 'first':
            return dom_element[0]
        elif return_type == 'all':
            return dom_element
        elif return_type == 'last':
            return dom_element[-1]

    def check_login_page(self):
        '''
        Checks if the login page is displayed in the browser.

        Returns:
            bool: True if the login page is not present, False otherwise.
        '''
        login_button = self.browser.find_elements(By.XPATH, self.markers.login_xq)
        return len(login_button) == 0

    def sleepy_find_element(self, by: By, query: str, attempt_count: int = 20, sleep_dur: int = 1):
        '''
        Finds the web element using the locator and query.

        This function attempts to find the element multiple times with a specified
        sleep duration between attempts. If the element is found, the function returns the element.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            query (str): The query string to locate the element.
            attempt_count (int, optional): The number of attempts to find the element. Default: 20.
            sleep_dur (int, optional): The duration to sleep between attempts. Default: 1.

        Returns:
            selenium.webdriver.remote.webelement.WebElement: Web element or None if not found.
        '''
        for _count in range(attempt_count):
            item = self.browser.find_elements(by, query)
            if len(item) > 0:
                item = item[0]
                logging.info('Element %s has found', query)
                break
            logging.info('Element %s is not present, attempt: %d', query, _count+1)
            time.sleep(sleep_dur)
        return item

    def wait_until_appear(self, by : By, query : str):
        '''
        Waits until the specified web element appears on the page.

        This function continuously checks for the presence of a web element.
        It waits until the element is present on the page.
        Once the element has appeared, the function returns.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            query (str): The query string to locate the element.
            timeout_dur (int, optional): Waiting time before the timeout. Default: 15.

        Returns:
            None
        '''
        logging.info('Waiting element %s to appear.', query)
        try:
            element = self.wait_object.until(
                EC.presence_of_element_located((by, query))
            )
            logging.info('Element %s appeared.', query)
        except Exceptions.TimeoutException:
            logging.info('Element %s is not present, something is wrong.', query)
        return element

    def wait_until_disappear(self, by : By, query : str):
        '''
        Waits until the specified web element disappears from the page.

        This function continuously checks for the presence of a web element.
        It waits until the element is no longer present on the page.
        Once the element has disappeared, the function returns.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            query (str): The query string to locate the element.
            timeout_dur (int, optional): Waiting time before the timeout. Default: 15.

        Returns:
            None
        '''
        logging.info('Waiting element %s to disappear.', query)
        try:
            self.wait_object.until_not(
                EC.presence_of_element_located((by, query))
            )
            logging.info('Element %s disappeared.', query)
        except Exceptions.TimeoutException:
            logging.info('Element %s still here, something is wrong.', query)
        return

    def log_chat(self, question : str, answer : str) -> bool:
        """
        Log a chat interaction in the chat history.

        Parameters:
        - question (str): The user's question to be logged.
        - answer (str): The answer to the user's question to be logged.

        Returns:
        - bool: True if the interaction is logged, False otherwise.
        """
        if self.auto_save:
            self.chat_history.loc[len(self.chat_history)] = ['user', False, question]
            self.chat_history.loc[len(self.chat_history)] = [self.client_name, False, answer]
            return True
        return False

    def preload_custom_func(self) -> None:
        """
        A function to implement specific instructions before loading the webpage
        """
        logging.info(
            '''
            The preload behavior is not implemented,
            which could be considered normal if verification is not required.
            '''
        )

    def postload_custom_func(self) -> None:
        """
        A function to implement specific instructions after loading the webpage
        """
        logging.info(
            '''
            The postload behavior is not implemented,
            which could be considered normal if verification is not required.
            '''
        )

    def pass_verification(self) -> bool:
        '''
        Performs the verification process on the page if challenge is present.
        Returns:
            None
        '''
        logging.info(
            '''
            Pass verification function is not implemented,
            which could be considered normal if verification is not required.
            '''
        )
        return True

    @abc.abstractmethod
    def login(self, username: str, password: str) -> bool:
        '''
        Performs the login process with the provided username and password.
        '''
        logging.warning('If you are creating a custom automation, please implement this method!')

    @abc.abstractmethod
    def interact(self, question : str) -> str:
        '''
        Abstract function to interact with the language model.
        '''
        logging.warning('If you are creating a custom automation, please implement this method!')

    @abc.abstractmethod
    def reset_thread(self) -> bool:
        '''
        Abstract function to open a new thread.
        '''
        logging.warning('Resetting thread is either not implemented or not available')

    @abc.abstractmethod
    def regenerate_response(self) -> str:
        '''
        Abstract function to regenerate the answers.
        '''
        logging.warning('Regenerating response is either not implemented or not available')

    @abc.abstractmethod
    def switch_model(self, model_name : str) -> bool:
        '''
        Abstract function to switch the model.

        Args:
            model_name: (str) = The name of the model.
        '''
        logging.warning('Switching model is either not implemented or not available')
