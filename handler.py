"""Class definition for ChatGPT Handler"""

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class Handler:
    """Handler class to interact with ChatGPT"""

    login_xq = '//button[text()="Log in"]'
    continue_xq = '//button[text()="Continue"]'
    next_xq = '//button[text()="Next"]'
    done_xq = '//button[text()="Done"]'

    chatbox_cq = 'text-sm'
    answer_cq = 'group'
    wait_cq = 'text-2xl'
    reset_xq = '//a[text()="Reset Thread"]'

    def __init__(self, username: str, password: str,
                 headless: bool = True,
                 experimental_options: dict = None):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', experimental_options or {})
        options.add_argument("--incognito")
        if headless:
            options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=options)
        self.browser.set_page_load_timeout(15)

        self.browser.get("https://chat.openai.com/chat")
        self.login(username, password)

    def login(self, username:str, password:str):
        """To enter system"""
        # Find login button, click it
        login_button = self.browser.find_element(By.XPATH, self.login_xq)
        login_button.click()
        time.sleep(1)

        # Find email textbox, enter e-mail
        email_box = self.browser.find_element(By.ID, "username")
        email_box.send_keys(username)
        # Click continue
        continue_button = self.browser.find_element(By.XPATH, self.continue_xq)
        continue_button.click()
        time.sleep(1)

        # Find password textbox, enter password
        pass_box = self.browser.find_element(By.ID, "password")
        pass_box.send_keys(password)
        # Click continue
        continue_button = self.browser.find_element(By.XPATH, self.continue_xq)
        continue_button.click()
        time.sleep(1)

        # Pass introduction
        next_button = self.browser.find_element(By.XPATH, self.next_xq)
        next_button.click()
        next_button = self.browser.find_element(By.XPATH, self.next_xq)
        next_button.click()
        done_button = self.browser.find_element(By.XPATH, self.done_xq)
        done_button.click()

    def interact(self, question: str):
        """Function to get an answer for a question"""
        text_area = self.browser.find_element(By.TAG_NAME, 'textarea')
        for each_line in question.split("\n"):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)
        while True:
            thinking = self.browser.find_elements(
                By.CLASS_NAME, self.wait_cq)
            if len(thinking) == 0:
                break
            time.sleep(1)
        box = self.browser.find_elements(By.CLASS_NAME, self.chatbox_cq)[0]
        answer = box.find_elements(By.CLASS_NAME, self.answer_cq)[-1]
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

    chatgpt = Handler(args.username, args.password)
    result = chatgpt.interact("Hello, how are you today")
    print(result)
