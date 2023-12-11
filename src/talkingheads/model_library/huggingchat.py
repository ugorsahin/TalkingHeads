'''Class definition for HuggingChat client'''
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from ..base_browser import BaseBrowser

class HuggingChatClient(BaseBrowser):
    '''
    HuggingChatClient class to interact with HuggingChat.
    It helps you to conncet to https://huggingface.co/chat/ and login.
    Apart from core functionality HuggingChat supports web search.
    It is not possible to regenerate a response by using HuggingChat
    '''

    def __init__(self, **kwargs):
        super().__init__(
            client_name='HuggingChat',
            url='https://huggingface.co/chat/',
            uname_env_var='HUGGINGCHAT_UNAME',
            pwd_env_var='HUGGINGCHAT_PWD',
            timeout_dur=45,
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
            bool : True if login is successful
        '''

        # Find login button, click it
        login_button = self.sleepy_find_element(By.XPATH, self.markers.login_xq)
        login_button.submit()
        logging.info('Clicked login button')

        # Find email textbox, enter e-mail
        email_box = self.sleepy_find_element(By.XPATH, self.markers.username_xq)
        email_box.send_keys(username)
        logging.info('Filled username/email')

        # Find password textbox, enter password
        pass_box = self.sleepy_find_element(By.XPATH, self.markers.password_xq)
        pass_box.send_keys(password)
        logging.info('Filled password box')

        # Click continue
        a_login_button = self.sleepy_find_element(By.XPATH, self.markers.a_login_xq)
        a_login_button.click()
        logging.info('Clicked login button')
        return True

    def interact(self, question : str):
        '''Sends a question and retrieves the answer from the ChatGPT system.
        
        This function interacts with the HuggingChat.
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
        self.wait_until_disappear(By.XPATH, self.markers.stop_gen_xq)
        answer = self.find_or_fail(By.XPATH, self.markers.chatbox_xq, return_type='last')
        if not answer:
            return ''
        logging.info('Answer is ready')
        self.log_chat(question=question, answer=answer.text)
        return answer.text

    def reset_thread(self):
        '''Function to close the current thread and start new one'''
        self.browser.get(self.url)
        return True

    def toggle_search_web(self):
        """Function to enable/disable web search feature"""
        search_web_toggle = self.find_or_fail(By.XPATH, self.markers.search_xq)
        if not search_web_toggle:
            return
        search_web_toggle.click()
        status = search_web_toggle.get_attribute('aria-checked')
        status = status == "true"
        logging.info('Search web is %s', ["disabled", "enabled"][status])
        return status

    def switch_model(self, model_name : str):
        '''
        Switch the model.

        Args:
            model_name: str = The name of the model

        Returns:
            bool: True on success, False on fail
        '''
        model_button = self.find_or_fail(By.XPATH, self.markers.model_xq)
        if not model_button:
            return False
        model_button.click()

        self.wait_object.until(
            EC.presence_of_element_located((By.XPATH, self.markers.settings_xq))
        )
        models = self.find_or_fail(By.XPATH, self.markers.model_li_xq, return_type='all')
        if not models:
            return False
        models = {m.text.strip():m for m in models}

        model = models.get(model_name, None)
        if model is None:
            logging.error('Model %s has not found', model_name)
            logging.error('Available models are: %s', str(models.keys()))
            return False

        model.click()
        logging.info('Switched to %s', model_name)

        apply_button = self.find_or_fail(By.XPATH, self.markers.model_a_xq)
        if not apply_button:
            return False

        apply_button.click()
        return True

    def regenerate_response(self):
        raise NotImplementedError(
            'HuggingChat doesn\'t provide response regeneration')
