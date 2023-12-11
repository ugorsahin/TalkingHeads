'''Class definition for PI client'''
import logging
import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from ..base_browser import BaseBrowser

class PiClient(BaseBrowser):
    '''
    PiClient class to interact with Pi.
    It helps you to conncet to https://pi.ai/.
    Apart from core functionality Pi supports web search.
    It is not possible to regenerate a response by using Pi
    '''

    def __init__(self, **kwargs):
        super().__init__(
            client_name='Pi',
            url='https://pi.ai/talk',
            uname_env_var='PI_UNAME',
            pwd_env_var='PI_PWD',
            credential_check=False,
            **kwargs
        )

    def login(self, username : str = None, password : str = None):
        '''
        Performs the login process with the provided username and password.
        You don't need to login to use Pi

        This function operates on the login page.
        It finds and clicks the login button,
        fills in the email and password textboxes

        Args:
            username (str): The username to be entered.
            password (str): The password to be entered.

        Returns:
            bool : True
        '''
        logging.info('Login is not provided for Pi at the moment.')
        return True

    def postload_custom_func(self) -> None:
        '''Pi starts with a welcome message, we should wait until the message to finish.'''
        time.sleep(2)
        self.browser.get(self.url)
        self.is_ready_to_prompt()
        return

    def is_ready_to_prompt(self) -> bool:
        '''
        Checks if the Pi is ready to be prompted.
        The indication for an ongoing message generation process
        is a disabled send button. The indication for no input is the same
        disabled button. Therefore we put a dummy dot into the textarea
        and we are left with the only reason for the button to be disabled,
        that is, a message being generated.

        Returns:
            bool : return if the system is ready to be prompted.
        '''

        text_area = self.wait_until_appear(By.XPATH, self.markers.textarea_xq)
        if not text_area:
            return False
        text_area.send_keys('.')
        self.wait_until_disappear(By.XPATH, self.markers.wait_xq)

        # Then, we clear the text area to make space for new interacton :)
        text_area.send_keys(Keys.CONTROL + "a")
        time.sleep(0.1)
        text_area.send_keys(Keys.DELETE)
        time.sleep(0.1)
        return True

    def interact(self, question : str):
        '''Sends a question and retrieves the answer from the ChatGPT system.
        
        This function interacts with the PI.
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

        self.find_or_fail(By.XPATH, self.markers.sendkeys_xq).click()
        logging.info('Message sent, waiting for response')

        if not self.is_ready_to_prompt():
            return False

        answer = self.find_or_fail(By.CLASS_NAME, self.markers.chatbox_cq, return_type='last')
        if not answer:
            return ''
        logging.info('Answer is ready')
        self.log_chat(question=question, answer=answer.text)
        return answer.text

    def reset_thread(self) -> bool:
        '''
        Function to close the current thread and start new one
        
        Returns:
            bool: False always, it is not possible to reset in Pi.
        '''
        logging.info('Pi doesn\'t provide a way to reset the thread')
        return False

    def switch_model(self, model_name : str):
        '''
        Switch the model.

        Args:
            model_name: str = The name of the model

        Returns:
            bool: True on success, False on fail
        '''
        model_button = self.find_or_fail(By.XPATH, self.markers.model_1_xq)
        if not model_button:
            return False
        model_button.click()
        time.sleep(1)

        models = self.find_or_fail(By.XPATH, self.markers.model_2_xq, return_type='all')
        if not models:
            return False
        models = {model.text or 'Pi' : model for model in models}
        logging.info(models.keys())

        model = models.get(model_name, None)
        if model is None:
            logging.error('Model %s has not found', model_name)
            logging.error('Available models are: %s', str(models.keys()))
            return False
        model.click()

        verification = self.find_or_fail(By.XPATH, self.markers.model_v_xq)
        if not re.search(fr'Switched to( just)? {model_name}', verification.text):
            logging.error('Model switch to %s is unsuccessful', model_name)
            return False

        logging.info('Switched to %s', model_name)
        return True

    def regenerate_response(self):
        raise NotImplementedError('Pi doesn\'t provide response regeneration')
