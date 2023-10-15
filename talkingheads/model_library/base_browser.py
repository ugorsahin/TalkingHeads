'''Class definition for ChatGPT_Client'''

import os
import logging
import time
from datetime import datetime
import undetected_chromedriver as uc
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as Exceptions

from .helpers import detect_chrome_version, save_func_map

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.WARNING
)

class BaseBrowser:
    '''BaseBrowser class to provide utility function and flow for LLMs'''

    def __init__(
        self,
        client_name : str = None,
        url : str = None,
        uname_env_var : str = None,
        pwd_env_var : str = None,
        username: str = '',
        password: str = '',
        headless: bool = True,
        cold_start: bool = False,
        incognito: bool = True,
        driver_executable_path :str =None,
        driver_arguments: list = None,
        driver_version: int = None,
        auto_save: bool = False,
        save_path: str = None,
        verbose: bool = False,
        credential_check: bool = True,
        skip_login: bool = False,
        user_data_dir: str = None
    ):
        self.client_name    = client_name
        self.url            = url
        self.uname_env_var  = uname_env_var
        self.pwd_env_var    = pwd_env_var

        if not skip_login and credential_check:
            if username or password:
                logging.warning(
                    "The usage of username and password parameters are deprecated and will be removed in near feature."
                    "Please adjust your environment variables to pass username and password."
                )

            username = username or os.environ.get(self.uname_env_var)
            password = password or os.environ.get(self.pwd_env_var)

            if not username:
                logging.error(f'Either provide username or set the environment variable "{self.uname_env_var}"')
                return

            if not password:
                logging.error(f'Either provide password or set the environment variable "{self.pwd_env_var}"')
                return

        if verbose:
            logging.getLogger().setLevel(logging.INFO)
            logging.info('Verbose mode active')
        options = uc.ChromeOptions()
        if incognito:
            options.add_argument('--incognito')
        if headless:
            options.add_argument('--headless')
        if driver_arguments:
            for _arg in driver_arguments:
                options.add_argument(_arg)

        logging.info('Loading undetected Chrome')
        self.browser = uc.Chrome(
            user_data_dir=user_data_dir,
            driver_executable_path=driver_executable_path,
            options=options,
            headless=headless,
            version_main=detect_chrome_version(driver_version),
            log_level=10,
        )
        self.browser.set_page_load_timeout(15)
        if cold_start:
            return

        logging.info('Loaded Undetected chrome')
        logging.info(f'Opening {self.client_name}')

        self.preload_custom_func()
        self.browser.get(self.url)
        self.postload_custom_func()
        self.pass_verification()
        if not skip_login:
            self.login(username, password)

        logging.info(f'{self.client_name} is ready to interact')

        self.chat_history = pd.DataFrame(columns=['role', 'is_regen', 'content'])
        self.auto_save = auto_save
        self.set_save_path(save_path)

    # def __del__(self):
    #     logging.info(f'{self.client_name} Instance is being deleted')
    #     if self.auto_save:
    #         self.save()

    def set_save_path(self, save_path):
        """Sets the path to save the file

        Args:
            save_path (str): The saving path
        """
        self.save_path = save_path or datetime.now().strftime('%Y_%m_%d_%H_%M_%S.csv')
        self.file_type = save_path.split('.')[-1] if save_path else 'csv'

    def save(self):
        """Saves the conversation."""
        save_func = save_func_map.get(self.file_type, None)
        if save_func:
            save_func = getattr(self.chat_history, save_func)
            save_func(self.save_path)
            logging.info(f'File saved to {self.save_path}')
        else:
            logging.error(f'Unsupported file type {self.file_type}')

    def find_or_fail(self, by, query, return_all_elements=False, fail_ok=False):
        """Finds a list of elements given query, if none of the items exists, throws an error

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            query (str): The query string to locate the element.

        Returns:
            selenium.webdriver.remote.webelement.WebElement: Web element or None if not found.
        """
        dom_element = self.browser.find_elements(by, query)
        if not dom_element:
            if not fail_ok:
                logging.error(f'{query} is not located. Please raise an issue with verbose=True')
            else:
                logging.info(f'{query} is not located.')
            return None

        logging.info(f'{query} is located.')
        if return_all_elements:
            return dom_element
        else:
            return dom_element[0]

    def check_login_page(self):
        '''
        Checks if the login page is displayed in the browser.

        Returns:
            bool: True if the login page is not present, False otherwise.
        '''
        login_button = self.browser.find_elements(By.XPATH, self.login_xq)
        return len(login_button) == 0

    def sleepy_find_element(self, by, query, attempt_count :int =20, sleep_duration :int =1):
        '''
        Finds the web element using the locator and query.

        This function attempts to find the element multiple times with a specified
        sleep duration between attempts. If the element is found, the function returns the element.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            query (str): The query string to locate the element.
            attempt_count (int, optional): The number of attempts to find the element. Default: 20.
            sleep_duration (int, optional): The duration to sleep between attempts. Default: 1.

        Returns:
            selenium.webdriver.remote.webelement.WebElement: Web element or None if not found.
        '''
        for _count in range(attempt_count):
            item = self.browser.find_elements(by, query)
            if len(item) > 0:
                item = item[0]
                logging.info(f'Element {query} has found')
                break
            logging.info(f'Element {query} is not present, attempt: {_count+1}')
            time.sleep(sleep_duration)
        return item

    def wait_until_disappear(self, by, query, timeout_duration=15):
        '''
        Waits until the specified web element disappears from the page.

        This function continuously checks for the presence of a web element.
        It waits until the element is no longer present on the page.
        Once the element has disappeared, the function returns.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            query (str): The query string to locate the element.
            timeout_duration (int, optional): The total wait time before the timeout exception. Default: 15.

        Returns:
            None
        '''
        logging.info(f'Waiting element {query} to disappear.')
        try:
            WebDriverWait(
                self.browser,
                timeout_duration
            ).until_not(
                EC.presence_of_element_located((by, query))
            )
            logging.info(f'Element {query} disappeared.')
        except Exceptions.TimeoutException:
            logging.info(f'Element {query} still here, something is wrong.')
        return

    def preload_custom_func(self):
        """
        Implement specific settings for a LLM.
        """
        logging.info('Preload behaviour is not implemented, that may be normal if verification is not necessary')
        return

    def postload_custom_func(self):
        """
        Implement specific settings for a LLM.
        """
        logging.info('Postload behaviour is not implemented, that may be normal if verification is not necessary')
        return

    def pass_verification(self):
        '''
        Performs the verification process on the page if challenge is present.
        Returns:
            None
        '''
        logging.info('Verification is not implemented, that may be normal if verification is not necessary')
        return

    def login(self, username: str, password: str):
        '''
        Performs the login process with the provided username and password.
        '''
        raise NotImplementedError(
            'If you are creating a custom automation, please implement this method!')

    def interact(self, question : str):
        raise NotImplementedError(
            'If you are creating a custom automation, please implement this method!')

    def reset_thread(self):
        raise NotImplementedError(
            'Resetting thread is either not implemented or not available for this LLM')

    def regenerate_response(self):
        raise NotImplementedError(
            'Regenerating response is either not implemented or not available for this LLM')

    def switch_model(self, model_name : str):
        raise NotImplementedError(
            'Switching model is either not implemented or not available for this LLM')
