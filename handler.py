"""Class definition for ChatGPT Handler"""

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Handler:
    """Handler class to interact with ChatGPT"""

    dialog_finder = '//div[contains(@class, "ConversationItem__Message")]'
    button_finder = '//div[contains(@class, "PromptTextarea__TextareaWrapper")]'

    def __init__(self, username, password):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {})
        options.add_argument("--incognito")
        options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=options)
        self.browser.set_page_load_timeout(15)

        self.browser.get("https://chat.openai.com/chat")
        self.login(username, password)

    def login(self, username, password):
        """To enter system"""
        login_button = self.browser.find_element(
            By.XPATH, '//button[text()="Log in"]')
        login_button.click()
        time.sleep(1)
        email_box = self.browser.find_element(By.ID, "username")
        email_box.send_keys(username)
        continue_button = self.browser.find_element(
            By.XPATH, '//button[text()="Continue"]')
        continue_button.click()
        time.sleep(1)
        pass_box = self.browser.find_element(By.ID, "password")
        pass_box.send_keys(password)
        continue_button = self.browser.find_element(
            By.XPATH, '//button[text()="Continue"]')
        continue_button.click()
        time.sleep(1)
        next_button = self.browser.find_element(
            By.XPATH, '//button[text()="Next"]')
        next_button.click()
        next_button = self.browser.find_element(
            By.XPATH, '//button[text()="Next"]')
        next_button.click()
        done_button = self.browser.find_element(
            By.XPATH, '//button[text()="Done"]')
        done_button.click()

    def interact(self, question):
        """Function to get an answer for a question"""
        text_area = self.browser.find_element(By.TAG_NAME, 'textarea')
        for each_line in question.split("\n"):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)
        while True:
            thinking = self.browser.find_element(By.XPATH, self.button_finder).find_element(
                By.TAG_NAME, 'button').find_elements(By.TAG_NAME, 'div')
            if len(thinking) == 0:
                break
            time.sleep(1)
        answer = self.browser.find_elements(By.XPATH, self.dialog_finder)[-1]
        return answer.text

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    parser.add_argument("password")
    args = parser.parse_args()

    chatgpt = Handler(args.username, args.password)
    result = chatgpt.interact("Hello, how are you today")
    print(result)
