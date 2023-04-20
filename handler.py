"""Class definition for ChatGPT Handler"""

import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as Exceptions
import re
import unicodedata
from cleantext import clean
from selenium.common.exceptions import TimeoutException

class TalkingHeads:
    """An interface for talking heads"""
    def __init__(self, username: str, password: str, headless=False, head_count=2):
        self.head_count=head_count
        self.driver = Handler(username, password, headless)
        for _ in range(head_count-1):
            self.driver.browser.execute_script(
                '''window.open("https://chat.openai.com/chat","_blank");''')
            time.sleep(1)

        self.head_responses = [[] for _ in range(head_count)]

    def switch_to_tab(self, idx: int = 0):
        "Switch to tab"
        windows = self.driver.browser.window_handles
        if idx > len(windows):
            print(f"There is no tab with index {idx}")
            return
        self.driver.browser.switch_to.window(windows[idx])

    def interact(self, head_number, question):
        """interact with the given head"""
        self.switch_to_tab(head_number)
        response = self.driver.interact(question)
        return response

    def reset_thread(self, head_number):
        """reset heads for the given number"""
        self.heads[head_number].reset_thread()
    
    def reset_all_threads(self):
        """reset heads for the given number"""
        for head in range(self.head_count):
            self.switch_to_tab(head)
            head.reset_thread()

    def start_conversation(self, text_1: str, text_2: str, use_response_1: bool= True):
        """Starts a conversation between two heads"""
        # assert len(self.heads) >= 2, "At least 2 heads is neccessary for a conversation"

        f_response = self.interact(0, text_1)
        text_2 = text_2 + f_response if use_response_1 else text_2
        s_response = self.interact(1, text_2)

        self.head_responses[0].append(f_response)
        self.head_responses[1].append(s_response)

        return f_response, s_response

    def continue_conversation(self, text_1: str= None, text_2: str= None):
        """Make another round of conversation.
        If text_1 or text_2 is given, the response is not used"""
        text_1 = text_1 or self.head_responses[1][-1]

        f_response = self.interact(0, text_1)
        text_2 = text_2 or f_response

        s_response = self.interact(1, text_2)

        self.head_responses[0].append(f_response)
        self.head_responses[1].append(s_response)
        return f_response, s_response
    
    def delete_all_conversations(self):
        for i in range(2):
            self.switch_to_tab(i)
            self.driver.delete_current_conversation()
        
class Handler:
    """Handler class to interact with ChatGPT"""
    def __init__(self, username :str, password :str,
        headless :bool = True, cold_start :bool = False):
        options = uc.ChromeOptions()
        options.add_argument("--incognito")
        if headless:
            options.add_argument("--headless")
        self.browser = uc.Chrome(options=options)
        self.browser.set_page_load_timeout(15)  
        self.wait: WebDriverWait= WebDriverWait(self.browser, 10)
        self.fetch_url("https://chat.openai.com/auth/login?next=/chat")
        if not cold_start:
            self.pass_verification()
            self.login(username, password)
    def check_login_page(self):
        login_button = self.browser.find_elements(By.XPATH, '//button[//div[text()="Log in"]]')
        return len(login_button) == 0
    def pass_verification(self):
        while self.check_login_page():
            verify_button = self.browser.find_elements(By.ID, 'challenge-stage')
            if len(verify_button):
                try:
                    verify_button[0].click()
                except Exceptions.ElementNotInteractableException:
                    pass
            time.sleep(1)
        return
    def fetch_url(self, url):
        self.browser.get(url)

    def wait_for_element_to_be_clickable_and_visible(self, xpath):
        self.wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH, xpath
                )
            )
        )
        time.sleep(0.2)
        return self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH, xpath
                )
            )
        )

    def login(self, username :str, password :str):
        """To enter system"""
        self.wait_for_element_to_be_clickable_and_visible('//button[//div[text()="Log in"]][1]').click()
        self.wait_for_element_to_be_clickable_and_visible('//input[@class="input cb739a8a3 c95effeb5"]').send_keys(username)
        self.browser.find_element(By.XPATH, '//button[text()="Continue"]').click()
        self.wait_for_element_to_be_clickable_and_visible('//input[@class="input cb739a8a3 c88749ff1"]').send_keys(password)
        self.browser.find_element(By.XPATH, '//button[text()="Continue"]').click()
        
        # Pass introduction
        self.wait_for_element_to_be_clickable_and_visible('//*[@id="headlessui-dialog-panel-:r1:"]/div[2]/div[4]/button/div').click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="headlessui-dialog-panel-:r1:"]/div[2]/div[4]/button[2]/div'))).click()
        self.wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="headlessui-dialog-panel-:r1:"]/div[2]/div[4]/button[2]' ))).click()

    def wait_to_disappear(self, by, query, sleep_duration=1):
        """Wait until the item disappear, then return"""
        while True:
            thinking = self.browser.find_elements(by, query)
            if len(thinking) == 0:
                break
            time.sleep(sleep_duration)
        return

    def check_if_request_limit_exceeded(self):
        elements = self.browser.find_elements(By.XPATH,'//div[@class="py-2 px-3 border text-gray-600 rounded-md text-sm dark:text-gray-100 border-red-500 bg-red-500/10"]')
        if len(elements) != 0:
            raise RequestLimitExceeded('Too many requests in 1 hour. Try again later.')
        
    def interact(self, question : str):
        """Function to get an answer for a question"""
        text_area = self.browser.find_element(By.TAG_NAME, 'textarea')
        for each_line in clean(question, no_emoji=True).split("\n"): # remove emojis because selenium can't handle them
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)
        self.check_if_request_limit_exceeded()
        self.wait_to_disappear(By.CLASS_NAME, 'text-2xl')
        answer = self.browser.find_elements(By.CLASS_NAME, 'text-base')[-1]
        return answer.text

    def reset_thread(self):
        """the conversation is refreshed"""
        self.browser.find_element(By.XPATH,'//a[text()="New chat"]').click()

    def delete_current_conversation(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH, '(//button[@class="p-1 hover:text-white"])[2]'))).click()    
        self.wait.until(EC.presence_of_element_located((By.XPATH, '(//button[@class="p-1 hover:text-white"])[1]'))).click()    
        
    def close_webdriver(self):
        self.browser.quit()
class RequestLimitExceeded(Exception):
    pass
