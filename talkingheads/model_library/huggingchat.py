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

class HuggingChatClient(BaseBrowser):
    '''HuggingChatClient class to interact with HuggingChat'''
    login_xq    = '//form[@action="/chat/login"]'
    username_xq = '//input[@name="username"]'
    password_xq = '//input[@name="password"]'
    a_login_xq  = '//button[contains(text(), "Login")]'

    textarea_xq = '//textarea[@enterkeyhint="send"]'
    stop_gen_xq = '//button[contains(text(),"Stop generating")]'
    chatbox_xq  = '//div[@role="presentation"]'
    search_xq   = '//div[@aria-label="web search toggle"]'

    model_xq    = '//div[div/div/text()="Current Model"]//button'
    model_li_xq = '//label'
    model_a_xq  = '//button[contains(text(), "Apply")]'

    def __init__(self, **kwargs):
        super().__init__(
            client_name='HuggingChat',
            url='https://huggingface.co/chat/',
            uname_env_var='HUGGINGCHAT_UNAME',
            pwd_env_var='HUGGINGCHAT_PWD',
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

        # Find login button, click it
        login_button = self.sleepy_find_element(By.XPATH, self.login_xq)
        login_button.submit()
        logging.info('Clicked login button')

        # Find email textbox, enter e-mail
        email_box = self.sleepy_find_element(By.XPATH, self.username_xq)
        email_box.send_keys(username)
        logging.info('Filled username/email')

        # Find password textbox, enter password
        pass_box = self.sleepy_find_element(By.XPATH, self.password_xq)
        pass_box.send_keys(password)
        logging.info('Filled password box')

        # Click continue
        a_login_button = self.sleepy_find_element(By.XPATH, self.a_login_xq)
        a_login_button.click()
        logging.info('Clicked login button')

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
        self.wait_until_disappear(By.XPATH, self.stop_gen_xq, timeout_duration=30)
        answer = self.find_or_fail(By.XPATH, self.chatbox_xq, return_all_elements=True)
        if not answer:
            return ''
        answer = answer[-1]
        logging.info('Answer is ready')
        if self.auto_save:
            self.chat_history.loc[len(self.chat_history)] = ['user', False, question]
            self.chat_history.loc[len(self.chat_history)] = [self.client_name, False, answer.text]
        return answer.text

    def reset_thread(self):
        '''Function to close the current thread and start new one'''
        new_chat_button = self.browser.get(self.url)
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

    def switch_model(self, model_name : str):
        '''
        Switch the model.

        Args:
            model_name: str = The name of the model

        Returns:
            bool: True on success, False on fail
        '''
        model_button = self.find_or_fail(By.XPATH, self.model_xq)
        if not model_button:
            return
        model_button.click()

        models = self.find_or_fail(By.XPATH, self.model_li_xq, return_all_elements=True)
        if not models:
            return
        models = {m.get_attribute('aria-label'):m for m in models}

        model = models.get(model_name, None)
        if model is None:
            logging.error(f'Model {model_name} has not found')
            logging.error(f'Available models are: {list(models.keys())}')
        else:
            model.click()
            logging.info(f'Switched to {model_name}')

        apply_button = self.find_or_fail(By.XPATH, self.model_a_xq)
        if apply_button:
            apply_button.click()

        return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('password')
    args = parser.parse_args()

    huggingFace = HuggingChatClient(args.username, args.password)
    result = huggingFace.interact('Hello, how are you today')
    print(result)
