'''Class definition for BardClient'''
import logging
from typing import Union

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from talkingheads.base_browser import BaseBrowser

class BardClient(BaseBrowser):
    '''BardClient class to interact with Bard'''
    def __init__(self, **kwargs):
        super().__init__(
            client_name='Bard',
            url='https://bard.google.com/chat',
            credential_check=False,
            **kwargs
        )

    def login(self, username :str, password :str) -> bool:
        '''
        Performs the login process with the provided username and password.

        This function operates on the login page.
        It finds and clicks the login button,
        fills in the email and password textboxes

        Args:
            username (str): The username to be entered.
            password (str): The password to be entered.

        Returns:
            bool : True if login succesful, False otherwise.
        '''
        logging.info(
            'It is not possible to provide login functionality for Google'
            'Please follow the instructions on the repo to connect Bard'
        )
        text_area = self.find_or_fail(By.XPATH, self.markers.textarea_xq)
        if not text_area and not self.headless:
            for _ in range(5):
                logging.error(
                    '''Prompt area can\'t located, use browser to manually
                    login your account, navigate to https://bard.google.com/chat
                    and press any key here.''')
                input()
                text_area = self.find_or_fail(By.XPATH, self.markers.textarea_xq)
                break
            else:
                logging.error('Login is unsuccesful')
                return False
        return True

    def interact(self, question : str) -> str:
        '''
        Sends a question and retrieves the answer from the ChatGPT system.

        This function interacts with the Bard.
        It takes the question as input and sends it to the system.
        The question may contain multiple lines separated by '\\n'. 
        In this case, the function simulates pressing SHIFT+ENTER for each line.
        Upon arrival of the interaction, the function waits for the answer.
        Once the response is ready, the function will return the response.

        Args:
            question (str): The interaction text.

        Returns:
            str: The generated answer.
        '''

        text_area = self.find_or_fail(By.XPATH, self.markers.textarea_xq)
        if not text_area:
            return ''

        for each_line in question.split('\n'):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)
        logging.info('Message sent, waiting for response')
        self.wait_until_disappear(By.XPATH, self.markers.wait_xq)
        answer = self.find_or_fail(By.TAG_NAME, self.markers.chatbox_tq, return_type='last')
        if not answer:
            logging.info('Answer is not found.')
            return ''

        logging.info('Answer is ready')
        self.log_chat(question=question, answer=answer.text)
        return answer.text

    def reset_thread(self) -> bool:
        '''Function to close the current thread and start new one

        Returns:
            bool: True new chat button is clicked, false otherwise
        '''
        new_chat_button = self.find_or_fail(By.XPATH, self.markers.new_chat_xq)
        if not new_chat_button:
            return False

        new_chat_button.click()
        logging.info('New chat is ready')
        return True

    def toggle_search_web(self) -> Union[bool, None]:
        '''Function to enable/disable web search feature
        
        Returns:
            [bool, None] : The status of the web search functionality, None if toggle is not found.
        '''
        search_web_toggle = self.find_or_fail(By.XPATH, self.markers.search_xq)
        if not search_web_toggle:
            return None
        search_web_toggle.click()
        state = search_web_toggle.get_attribute('aria-checked')
        state = state == "true"
        logging.info('Search web is %s', ["disabled", "enabled"][state])
        return state

    def regenerate_response(self) -> str:
        '''Closes the current thread and starts a new one.

        Args:
            None

        Returns:
            str: The regenerated answer or empty string in case of failure.
        '''
        view_drafts = self.find_or_fail(By.XPATH, self.markers.regen_1_xq)
        if not view_drafts:
            return
        view_drafts.click()
        logging.info('Clicked View drafts button')

        regen_button = self.find_or_fail(By.XPATH, self.markers.regen_2_xq)
        if not regen_button:
            return ''

        regen_button.click()
        logging.info('Clicked regenerate button')
        self.wait_until_disappear(By.XPATH, self.markers.wait_xq)
        answer = self.browser.find_elements(By.TAG_NAME, self.markers.chatbox_tq)[-1]
        logging.info('New answer is ready')

        if self.auto_save:
            self.chat_history.loc[len(self.chat_history)] = [self.client_name, True, answer.text]
        return answer.text

    def switch_model(self, model_name : str) -> bool:
        logging.info('Bard doesn\'t have a model selection')
        return False
