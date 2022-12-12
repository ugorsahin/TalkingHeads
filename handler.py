"""Class definition for ChatGPT Handler"""

import time
import undetected_chromedriver as uc

##from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Handler:
    """Handler class to interact with ChatGPT"""

    login_xq    = '//button[text()="Log in"]'
    continue_xq = '//button[text()="Continue"]'
    next_xq     = '//button[text()="Next"]'
    done_xq     = '//button[text()="Done"]'
    
    chatbox_cq  = 'text-sm'
    answer_cq   = 'group'
    wait_cq     = 'text-2xl'
    reset_xq    = '//a[text()="Reset Thread"]'

    def __init__(self, username :str, password :str,
        headless :bool = True):
        options = uc.ChromeOptions()
        options.add_argument("--incognito")
        if headless:
            options.add_argument("--headless")
        self.browser = uc.Chrome(options=options)
        self.browser.set_page_load_timeout(15)

        self.browser.get("https://chat.openai.com/chat")
        self.login(username, password)

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

        # Pass introduction
        next_button = self.sleepy_find_element(By.XPATH, self.next_xq)
        next_button.click()
        next_button = self.sleepy_find_element(By.XPATH, self.next_xq)
        next_button.click()
        done_button = self.sleepy_find_element(By.XPATH, self.done_xq)
        done_button.click()

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
        box = self.browser.find_elements(By.CLASS_NAME, self.chatbox_cq)[0]
        answer = box.find_elements(By.CLASS_NAME, self.answer_cq)[-1]
        return answer.text

    def reset_thread(self):
        """the conversation is refreshed"""
        self.browser.find_element(By.XPATH, self.reset_xq).click()

    def switch_to_tab(self, idx : int = 0):
        "Switch to tab"
        windows = self.browser.window_handles
        if idx > len(windows):
            print(f"There is no tab with index {idx}")
            return
        self.browser.switch_to.window(windows[idx])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    parser.add_argument("password")
    args = parser.parse_args()

    chatgpt = Handler(args.username, args.password)
    result = chatgpt.interact("Hello, how are you today")
    print(result)
