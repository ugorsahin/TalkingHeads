"""Class definition for ChatGPTClient"""

import os
import time
from datetime import datetime
import asyncio
from nodriver import cdp
from .. import BaseBrowser


class ChatGPTClient(BaseBrowser):
    """ChatGPTClient class to interact with ChatGPT"""

    custom_areas = {"name": 0, "occupation": 1, "modulation": 2, "extra_information": 3}

    def __init__(self, **kwargs):
        super().__init__(client_name="ChatGPT", url="https://chatgpt.com", **kwargs)

    async def postload_custom_func(self):
        pass

    async def pass_verification(self, max_trial: int = 10, wait_time: int = 1) -> bool:
        """
        Performs the verification process on the page if challenge is present.

        This function checks if the login page is displayed in the browser.
        In that case, it looks for the verification button.
        This process is repeated until the login page is no longer displayed.

        Returns: None
        """
        # for _ in range(max_trial):
        #     verify_button = self.find_or_fail("challenge-stage")
        #     if not verify_button:
        #         break
        #     try:
        #         verify_button[0].click()
        #         self.logger.info("Clicked verification button")
        #     except Exceptions.ElementNotInteractableException:
        #         self.logger.info("Verification button is not present or clickable")
        #     time.sleep(wait_time)
        # else:
        #     self.logger.error("It is not possible to pass verification")
        #     return False

        return True

    async def login(self) -> bool:
        """
        Performs the login process with the provided username and password.

        This function operates on the login page.
        It finds and clicks the login button,
        fills in the email and password textboxes

        Args:
            username (str): The username to be entered.
            password (str): The password to be entered.

        Returns:
            None
        """

        # Find login button, click it
        login_button = await self.wait_until_appear(self.markers.login)
        await login_button.click()

        # login_button = self.find_or_fail(self.markers.login, fail_ok=True)
        # login_button.click()
        self.logger.info("Clicked login button for the first time.")

        for _ in range(5):
            email_box = await self.wait_until_appear(
                self.markers.email, 5, fail_ok=True
            )
            if email_box:
                self.logger.info("Username area has found")
                break
            login_button = await self.find_or_fail(self.markers.login, fail_ok=True)

            if login_button:
                await login_button.click()
                self.logger.info("Trying to click login button once more")
        else:
            self.logger.error("Can't reach email page")
            return False

        await email_box.send_keys(os.environ.get(self.uname_var))
        self.logger.info("Filled email box")
        await email_box.send_keys('\r\n')

        # Find password textbox, enter password
        pass_box = await self.wait_until_appear(self.markers.pwd)
        await pass_box.send_keys(os.environ.get(self.pwd_var))
        self.logger.info("Filled password box")
        # Click continue

        continue_button = await self.wait_until_appear(self.markers.continue_btn)
        await continue_button.mouse_click()

        for _ in range(5):
            continue_button = await self.find_or_fail(
                self.markers.continue_btn, fail_ok=True
            )
            if continue_button:
                await continue_button.mouse_click()
                self.logger.info("Trying to click login button once more")
                time.sleep(2)
            else:
                break

        self.logger.info("Clicked continue in password page")

        tutorial = await self.find_or_fail(self.markers.tutorial, fail_ok=True)
        if tutorial:
            await tutorial.click()
            self.logger.info("Info screen passed")
        else:
            self.logger.info("Info screen skipped")

        text_area = await self.wait_until_appear(self.markers.textarea)

        if text_area is not None:
            self.logger.info("Login is successful.")
            return True

        self.logger.error("Login is not successful.")
        return False

    async def get_last_response(
        self, num_step: int = 200, period: float = 0.2, same_answer_limit=3
    ) -> str:
        """
        Continuously checks for a response in a chatbox-like element and
            returns the last received response.

        Args:
            num_step (int): Number of cycles to check for updates to the response.
                Defaults to 200.
            period (float): Sleep time between each step, representing the delay between each check.
                Defaults to 0.5 seconds.
            same_answer_limit (int): The maximum number of times the same response can
                be observed before concluding that the response is complete. Defaults to 3.

        Returns:
            str: The last valid response from the chatbox element.
                If no response is found, an empty string is returned.

        Behavior:
            - The function first waits for the chatbox element to appear on the page.
            - It continuously checks for updates to the response in the chatbox.
            - The response is checked continuously, `period` seconds between each check.
            - If the response remains the same for more than `same_answer_limit` consecutive times,
                the loop breaks, assuming the response is complete.
            - If no response is found, it returns an empty string.
            - If a response is found, it returns the last detected response.
        """

        self.logger.info("Checking the response")

        self.interim_response = None
        await self.wait_until_appear(self.markers.chatbox)
        counter = 0
        while (
            await self.find_or_fail(self.markers.stop, fail_ok=True)
            or counter < same_answer_limit
        ):
            l_response = await self.find_or_fail(
                self.markers.chatbox, return_type="last"
            )
            time.sleep(period)
            l_response = l_response.text_all if l_response else ""
            if l_response:
                counter = [0, counter + 1][l_response == self.interim_response]

            self.interim_response = l_response

        if not self.interim_response:
            self.logger.error("There is no response, something is wrong")
            return ""

        self.logger.info("response is ready")
        return self.interim_response

    async def toggle_search(self):
        search_button = await self.find_or_fail(self.markers.search)
        await search_button.click()
        search_button = await self.find_or_fail(self.markers.search)
        return search_button.attrs["aria-pressed"] == "true"

    async def toggle_reason(self):
        reason_button = await self.find_or_fail(self.markers.reason)
        await reason_button.click()
        reason_button = await self.find_or_fail(self.markers.reason)
        return reason_button.attrs["aria-pressed"] == "true"

    async def interact(self, prompt: str) -> str:
        """Sends a prompt and retrieves the response from the ChatGPT system.

        This function interacts with the ChatGPT.
        It takes the prompt as input and sends it to the system.
        The prompt may contain multiple lines separated by '\\n'.
        In this case, the function simulates pressing SHIFT+ENTER for each line.
        Upon arrival of the interaction, the function waits for the response.
        Once the response is ready, the function will return the response.

        Args:
            prompt (str): The interaction text.

        Returns:
            str: The generated response.
        """

        # prompt = prompt.replace("\n", "\r\n")
        text_area = await self.wait_until_appear(self.markers.textarea)
        if not text_area:
            raise RuntimeError(
                "Unable to find the text prompt area. Please raise an issue with verbose=True"
            )
        # await text_area.send_keys(prompt)
        await text_area.focus()
        await self.tab.send(cdp.input_.insert_text(text=prompt))

        send_button = await self.find_or_fail(self.markers.send)
        await send_button.click()

        response = await self.get_last_response()

        self.log_chat(prompt=prompt, response=response)
        return response

    async def reset_thread(self) -> bool:
        """Function to close the current thread and start new one"""
        await self.browser.get(self.url)
        text_area = await self.wait_until_appear(self.markers.textarea)
        if text_area:
            return True
        self.logger.error(
            "Couldn't reset the conversation. Please raise an issue with verbose=True"
        )
        return False

    async def regenerate_response(self) -> str:
        """
        Clicks the regenerate button to generate a new response
            and returns the new response.

        Args:
            None

        Returns:
            str: The newly generated response text. If the regeneration fails, returns an empty string.
        """
        regen_button = await self.find_or_fail(self.markers.regen_1)

        if not regen_button:
            return ""
        await regen_button.mouse_click()
        self.logger.info("Clicked regenerate button")

        try_again_button = await self.wait_until_appear(self.markers.regen_2)
        if not try_again_button:
            return ""
        await try_again_button.click()
        self.logger.info("Clicked Try again button")

        time.sleep(1)
        response = await self.get_last_response()
        if not response:
            self.logger.error("Regeneration failed")
            return ""

        self.log_chat(response=response, regenerated=True)
        return response

    async def open_custom_instruction_tab(self) -> bool:
        """Opens the modal to access custom interactions.

        Returns:
            bool: True if the process is successful, False otherwise
        """

        menu_button = await self.wait_until_appear(self.markers.menu)
        await menu_button.mouse_click()
        custom_button = await self.wait_until_appear(self.markers.custom)
        await custom_button.click()
        custom_tutorial = await self.find_or_fail(self.markers.cust_tut, fail_ok=True)
        if custom_tutorial:
            await custom_tutorial.click()

        custom_switch = await self.find_or_fail(self.markers.cust_toggle)
        if not custom_switch:
            return False

        # If disabled, enable custom interactions
        if custom_switch.attrs["data-state"] == "checked":
            self.logger.info("Custom instructions is enabled")
        else:
            await custom_switch.click()
        await asyncio.sleep(0.5)

        return True

    async def get_custom_instruction(self, mode: str) -> str:
        """Gets custom instructions

        Args:
            mode (str): Either 'extra_information' or 'modulation'. Check OpenAI help pages.
        """

        if mode not in self.custom_areas:
            self.logger.error(
                "Given mode is unrecognized. Possible keys are %s",
                ", ".join(self.custom_areas.keys()),
            )
            return ""

        if not await self.open_custom_instruction_tab():
            return ""

        await self.wait_until_appear(self.markers.cust_txt)
        text_areas = await self.find_or_fail(self.markers.cust_txt, return_type="all")
        await asyncio.sleep(1.)
        text = text_areas[self.custom_areas[mode]].text_all
        self.logger.info("Custom instruction is obtained: %s", text)

        cancel_button = await self.find_or_fail(self.markers.cust_cancel)
        await cancel_button.click()
        await self.wait_until_disappear(self.markers.cust_cancel)
        return text

    async def set_custom_instruction(self, mode: str, instruction: str):
        """Sets custom instructions

        Args:
            mode (str): Either 'extra_information' or 'modulation'. Check OpenAI help pages.
            instruction (str): _description_
        """

        if mode not in self.custom_areas:
            self.logger.error(
                "Given mode is unrecognized. Possible keys are %s",
                ", ".join(self.custom_areas.keys()),
            )
            return ""

        if not await self.open_custom_instruction_tab():
            return False

        await self.wait_until_appear(self.markers.cust_txt)
        text_areas = await self.find_or_fail(self.markers.cust_txt, return_type="all")
        text_area = text_areas[self.custom_areas[mode]]

        await BaseBrowser.clear_input(text_area)
        await text_area.send_keys(instruction)
        self.logger.info("Custom instruction-%s has provided", mode)

        save_button = await self.find_or_fail(self.markers.cust_save)
        await save_button.mouse_click()

        await self.wait_until_disappear(self.markers.cust_save)
        time.sleep(0.5)
        return True
