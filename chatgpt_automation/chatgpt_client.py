'''Class definition for ChatGPT_Client'''

import logging
import time
import undetected_chromedriver as uc

# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as Exceptions

from .helpers import find_chrome_version

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.WARNING
)

class ChatGPT_Client:
    '''ChatGPT_Client class to interact with ChatGPT'''

    login_xq    = '//button[//div[text()="Log in"]]'
    continue_xq = '//button[text()="Continue"]'
    next_cq     = 'prose'
    button_tq   = 'button'
    # next_xq     = '//button[//div[text()='Next']]'
    done_xq     = '//button[//div[text()="Done"]]'

    chatbox_cq  = 'text-base'
    wait_cq     = 'text-2xl'
    reset_xq    = '//a[text()="New chat"]'
    regen_xq    = '//div[text()="Regenerate response"]'

    def __init__(
        self,
        username :str,
        password :str,
        headless :bool = True,
        cold_start :bool = False,
        driver_executable_path :str =None,
        driver_arguments : list = None,
        verbose :bool = False
    ):
        if verbose:
            logging.getLogger().setLevel(logging.INFO)
            logging.info('Verbose mode active')
        options = uc.ChromeOptions()
        options.add_argument('--incognito')
        if headless:
            options.add_argument('--headless')
        if driver_arguments:
            for _arg in driver_arguments:
                options.add_argument(_arg)

        logging.info('Loading undetected Chrome')
        self.browser = uc.Chrome(
            driver_executable_path=driver_executable_path,
            options=options,
            headless=headless,
            version_main=find_chrome_version()
        )
        self.browser.set_page_load_timeout(15)
        logging.info('Loaded Undetected chrome')
        logging.info('Opening chatgpt')
        self.browser.get('https://chat.openai.com/auth/login?next=/chat')
        if not cold_start:
            self.pass_verification()
            self.login(username, password)
        logging.info('ChatGPT is ready to interact')

    def pass_verification(self):
        '''
        Performs the verification process on the page if challenge is present.

        This function checks if the login page is displayed in the browser.
        In that case, it looks for the verification button.
        This process is repeated until the login page is no longer displayed.

        Returns:
            None
        '''
        while self.check_login_page():
            verify_button = self.browser.find_elements(By.ID, 'challenge-stage')
            if len(verify_button):
                try:
                    verify_button[0].click()
                    logging.info('Clicked verification button')
                except Exceptions.ElementNotInteractableException:
                    logging.info('Verification button is not present or clickable')
            time.sleep(1)
        return

    def check_login_page(self):
        '''
        Checks if the login page is displayed in the browser.

        Returns:
            bool: True if the login page is not present, False otherwise.
        '''
        login_button = self.browser.find_elements(By.XPATH, self.login_xq)
        return len(login_button) == 0

    def login(self, username :str, password :str):
        '''
        Performs the login process with the provided username and password.

        This function operates on the login page.
        It finds and clicks the login button,
        fills in the email and password textboxes

        Args:
            username (str): The username to be entered.
            password (str): The password to be entered.

        Returns:
            None
        '''

        # Find login button, click it
        login_button = self.sleepy_find_element(By.XPATH, self.login_xq)
        login_button.click()
        logging.info('Clicked login button')
        time.sleep(1)

        # Find email textbox, enter e-mail
        email_box = self.sleepy_find_element(By.ID, 'username')
        email_box.send_keys(username)
        logging.info('Filled email box')

        # Click continue
        continue_button = self.sleepy_find_element(By.XPATH, self.continue_xq)
        continue_button.click()
        time.sleep(1)
        logging.info('Clicked continue button')

        # Find password textbox, enter password
        pass_box = self.sleepy_find_element(By.ID, 'password')
        pass_box.send_keys(password)
        logging.info('Filled password box')
        # Click continue
        continue_button = self.sleepy_find_element(By.XPATH, self.continue_xq)
        continue_button.click()
        time.sleep(1)
        logging.info('Logged in')

        try:
            # Pass introduction
            next_button = WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, self.next_cq))
            )
            next_button.find_elements(By.TAG_NAME, self.button_tq)[0].click()

            next_button = WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, self.next_cq))
            )
            next_button.find_elements(By.TAG_NAME, self.button_tq)[1].click()

            next_button = WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, self.next_cq))
            )
            next_button.find_elements(By.TAG_NAME, self.button_tq)[1].click()
            logging.info('Info screen passed')
        except Exceptions.TimeoutException:
            logging.info('Info screen skipped')
        except Exception as exp:
            logging.error(f'Something unexpected happened: {exp}')

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

    def wait_to_disappear(self, by, query, sleep_duration=1):
        '''
        Waits until the specified web element disappears from the page.

        This function continuously checks for the presence of a web element.
        It waits until the element is no longer present on the page.
        Once the element has disappeared, the function returns.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            query (str): The query string to locate the element.
            sleep_duration (int, optional): The duration to sleep between checks. Default: 1.

        Returns:
            None
        '''

        while True:
            thinking = self.browser.find_elements(by, query)
            if len(thinking) == 0:
                logging.info(f'Element {query} is present, waiting')
                break
            time.sleep(sleep_duration)
        return

    def interact(self, question : str):
        '''
        Sends a question and retrieves the answer from the ChatGPT system.

        This function interacts with the ChatGPT.
        It takes the question as input and sends it to the system.
        The question may contain multiple lines separated by '\n'. 
        In this case, the function simulates pressing SHIFT+ENTER for each line.

        After sending the question, the function waits for the answer.
        Once the response is ready, the response is returned.

        Args:
            question (str): The interaction text.

        Returns:
            str: The generated answer.
        '''
        text_area = self.browser.find_element(By.TAG_NAME, 'textarea')
        for each_line in question.split('\n'):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)
        logging.info('Message sent, waiting for response')
        self.wait_to_disappear(By.CLASS_NAME, self.wait_cq)
        answer = self.browser.find_elements(By.CLASS_NAME, self.chatbox_cq)[-1]
        logging.info('Answer is ready')
        return answer.text

    def reset_thread(self):
        '''Function to close the current thread and start new one'''
        self.browser.find_element(By.XPATH, self.reset_xq).click()
        logging.info('New thread is ready')

    def regenerate_response(self):
        '''
        Closes the current thread and starts a new one.

        Args:
            None

        Returns:
            None
        '''
        try:
            regen_button = self.browser.find_element(By.XPATH, self.regen_xq)
            regen_button.click()
            logging.info('Clicked regenerate button')
            self.wait_to_disappear(By.CLASS_NAME, self.wait_cq)
            answer = self.browser.find_elements(By.CLASS_NAME, self.chatbox_cq)[-1]
            logging.info('New answer is ready')
        except Exceptions.NoSuchElementException:
            logging.error('Regenerate button is not present')
        return answer

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('password')
    args = parser.parse_args()

    chatgpt = ChatGPT_Client(args.username, args.password)
    result = chatgpt.interact('Hello, how are you today')
    print(result)
