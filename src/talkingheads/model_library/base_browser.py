'''Class definition for ChatGPT_Client'''

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

from .utils import detect_chrome_version, save_func_map

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
        self.headless       = headless
        self.ready          = False
        self.auto_save = auto_save

        if not skip_login and credential_check:
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

    def save(self):
        """Saves the conversation."""
        save_func = save_func_map.get(self.file_type, None)
        if save_func:
            save_func = getattr(self.chat_history, save_func)
            save_func(self.save_path)
            logging.info('File saved to %s', self.save_path)
        else:
            logging.error('Unsupported file type %s', self.file_type)

    def find_or_fail(self, by : By, query : str, return_type : str = 'first', fail_ok : bool = False):
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
        login_button = self.browser.find_elements(By.XPATH, self.login_xq)
        return len(login_button) == 0

    def sleepy_find_element(self, by: By, query : str, attempt_count : int = 20, sleep_duration : int = 1):
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
                logging.info('Element %s has found', query)
                break
            logging.info('Element %s is not present, attempt: %d', query, _count+1)
            time.sleep(sleep_duration)
        return item

    def wait_until_disappear(self, by : By, query : str, timeout_duration : int = 15):
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
        logging.info('Waiting element %s to disappear.', query)
        try:
            WebDriverWait(
                self.browser,
                timeout_duration
            ).until_not(
                EC.presence_of_element_located((by, query))
            )
            logging.info('Element %s disappeared.', query)
        except Exceptions.TimeoutException:
            logging.info('Element %s still here, something is wrong.', query)
        return

    def save_turn(self, question : str, answer : str) -> bool:
        if self.auto_save:
            self.chat_history.loc[len(self.chat_history)] = ['user', False, question]
            self.chat_history.loc[len(self.chat_history)] = [self.client_name, False, answer]
            return True
        return False

    def preload_custom_func(self):
        """
        Implement specific settings for a LLM.
        """
        logging.info(
            'Preload behaviour is not implemented, that may be normal if verification is not necessary')
        return True

    def postload_custom_func(self):
        """
        Implement specific settings for a LLM.
        """
        logging.info(
            'Postload behaviour is not implemented, that may be normal if verification is not necessary')
        return True

    def pass_verification(self):
        '''
        Performs the verification process on the page if challenge is present.
        Returns:
            None
        '''
        logging.info(
            'Verification is not implemented, that may be normal if verification is not necessary')
        return True

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
