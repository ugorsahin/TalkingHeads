"""Class definition for ChatGPT_Client"""

import time
import undetected_chromedriver as uc

# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as Exceptions

class ChatGPT_Client:
    """ChatGPT_Client class to interact with ChatGPT"""

    login_xq    = '//button[//div[text()="Log in"]]'
    continue_xq = '//button[text()="Continue"]'
    next_cq     = 'prose'
    button_tq   = 'button'
    # next_xq     = '//button[//div[text()="Next"]]'
    done_xq     = '//button[//div[text()="Done"]]'

    chatbox_cq  = 'text-base'
    wait_cq     = 'text-2xl'
    reset_xq    = '//a[text()="New chat"]'

    def __init__(self, username :str, password :str,
        headless :bool = True, cold_start :bool = False):
        options = uc.ChromeOptions()
        options.add_argument("--incognito")
        if headless:
            options.add_argument("--headless")

        self.browser = uc.Chrome(
            # driver_executable_path='/usr/bin/google-chrome',
            options=options,
            headless=headless,
            version_main=112
        )
        self.browser.set_page_load_timeout(15)

        self.browser.get("https://chat.openai.com/auth/login?next=/chat")
        if not cold_start:
            self.pass_verification()
            self.login(username, password)


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

    def check_login_page(self):
        login_button = self.browser.find_elements(By.XPATH, self.login_xq)
        return len(login_button) == 0

    def login(self, username :str, password :str):
        """To enter system"""

        # Find login button, click it
        login_button = self.sleepy_find_element(By.XPATH, self.login_xq)
        login_button.click()
        time.sleep(1)

        # Find email textbox, enter e-mail
        email_box = self.sleepy_find_element(By.ID, "username")
        email_box.send_keys(username)

        # Click continue
        continue_button = self.sleepy_find_element(By.XPATH, self.continue_xq)
        continue_button.click()
        time.sleep(1)

        # Find password textbox, enter password
        pass_box = self.sleepy_find_element(By.ID, "password")
        pass_box.send_keys(password)
        # Click continue
        continue_button = self.sleepy_find_element(By.XPATH, self.continue_xq)
        continue_button.click()
        time.sleep(1)

        try:
            # Pass introduction
            next_button = self.browser.find_element(By.CLASS_NAME, self.next_cq)
            next_button = next_button.find_elements(By.TAG_NAME, self.button_tq)[0]
            next_button.click()
            time.sleep(1)
            next_button = self.browser.find_element(By.CLASS_NAME, self.next_cq)
            next_button = next_button.find_elements(By.TAG_NAME, self.button_tq)[1]
            next_button.click()
            time.sleep(1)
            next_button = self.browser.find_element(By.CLASS_NAME, self.next_cq)
            done_button = next_button.find_elements(By.TAG_NAME, self.button_tq)[1]
            done_button.click()
        except Exceptions.NoSuchElementException:
            pass

    def sleepy_find_element(self, by, query, attempt_count :int =20, sleep_duration :int =1):
        """If the loading time is a concern, this function helps"""
        for _ in range(attempt_count):
            item = self.browser.find_elements(by, query)
            if len(item) > 0:
                item = item[0]
                break
            time.sleep(sleep_duration)
        return item

    def wait_to_disappear(self, by, query, sleep_duration=1):
        """Wait until the item disappear, then return"""
        while True:
            thinking = self.browser.find_elements(by, query)
            if len(thinking) == 0:
                break
            time.sleep(sleep_duration)
        return

    def interact(self, question : str):
        """Function to get an answer for a question"""
        text_area = self.browser.find_element(By.TAG_NAME, 'textarea')
        for each_line in question.split("\n"):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)
        self.wait_to_disappear(By.CLASS_NAME, self.wait_cq)
        answer = self.browser.find_elements(By.CLASS_NAME, self.chatbox_cq)[-1]
        return answer.text

    def reset_thread(self):
        """the conversation is refreshed"""
        self.browser.find_element(By.XPATH, self.reset_xq).click()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    parser.add_argument("password")
    args = parser.parse_args()

    chatgpt = ChatGPT_Client(args.username, args.password)
    result = chatgpt.interact("Hello, how are you today")
    print(result)
