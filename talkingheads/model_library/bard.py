'''Class definition for ChatGPT_Client'''
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base_browser import BaseBrowser

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.WARNING
)

class BardClient(BaseBrowser):
    '''BardClient class to interact with Bard'''
    textarea_xq = '//div[@role="textbox"]'
    wait_xq     = '//img[contains(@src, "sparkle_thinking")]'
    chatbox_tq  = 'message-content'
    search_xq   = '//div[@aria-label="web search toggle"]'

    model_xq    = '//div[div/div/text()="Current Model"]//button'
    model_li_xq = '//label'
    model_a_xq  = '//button[contains(text(), "Apply")]'
    new_chat_xq = '//span[text()="New chat"]'
    regen_1_xq  = '//span[text()="View other drafts"]'
    regen_2_xq  = '//button[@mattooltip="Regenerate drafts"]'

    def __init__(self, **kwargs):
        super().__init__(
            client_name='Bard',
            url='https://bard.google.com/chat',
            credential_check=False,
            **kwargs
        )

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
        logging.info(
            'It is not possible to provide login functionality for Google'
            'Please follow the instructions on the repo to connect Bard'
        )
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

        text_area = self.find_or_fail(By.XPATH, self.textarea_xq)
        if not text_area:
            return ''

        for each_line in question.split('\n'):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)
        logging.info('Message sent, waiting for response')
        self.wait_until_disappear(By.XPATH, self.wait_xq)
        answer = self.find_or_fail(By.TAG_NAME, self.chatbox_tq, return_all_elements=True)[-1]
        logging.info('Answer is ready')
        if self.auto_save:
            self.chat_history.loc[len(self.chat_history)] = ['user', False, question]
            self.chat_history.loc[len(self.chat_history)] = [self.client_name, False, answer.text]
        return answer.text

    def reset_thread(self):
        '''Function to close the current thread and start new one'''
        new_chat_button = self.find_or_fail(By.XPATH, self.new_chat_xq)
        if new_chat_button:
            new_chat_button.click()
            logging.info('New chat is ready')
        return

    def toggle_search_web(self):
        """Function to enable/disable web search feature"""
        search_web_toggle = self.find_or_fail(By.XPATH, self.search_xq)
        if not search_web_toggle:
            return
        search_web_toggle.click()
        state = search_web_toggle.get_attribute('aria-checked')
        logging.info(f'Search web is {"enabled" if state == "true" else "disabled"}')
        return

    def regenerate_response(self):
        '''
        Closes the current thread and starts a new one.

        Args:
            None

        Returns:
            None
        '''
        view_drafts = self.find_or_fail(By.XPATH, self.regen_1_xq)
        if not view_drafts:
            return
        view_drafts.click()
        logging.info('Clicked View drafts button')

        regen_button = self.find_or_fail(By.XPATH, self.regen_2_xq)
        if not regen_button:
            return

        regen_button.click()
        logging.info('Clicked regenerate button')
        self.wait_until_disappear(By.XPATH, self.wait_xq)
        answer = self.browser.find_elements(By.TAG_NAME, self.chatbox_tq)[-1]
        logging.info('New answer is ready')

        if self.auto_save:
            self.chat_history.loc[len(self.chat_history)] = [self.client_name, True, answer.text]
        return answer.text

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('password')
    args = parser.parse_args()

    bard = BardClient()
    result = bard.interact('Hello, how are you today')
    print(result)
