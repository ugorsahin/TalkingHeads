from io import BytesIO
from re import sub
from ssl import OPENSSL_VERSION_NUMBER
from typing import KeysView, List
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse
import numpy as np
from undetected_chromedriver import ChromeOptions
import cv2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from constants import *
import random
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import *
import requests
from PIL import Image
from langdetect import detect

WAIT_TIME = 10
class BaseScraper:
    def __init__(self):
        self.driver = None
        self.load_driver()
        self.wait = WebDriverWait(self.driver, WAIT_TIME)

    def load_driver(self):
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.get_chrome_options(),
        )

    def get_chrome_options(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.headless = True
        chrome_options.add_experimental_option("prefs", prefs)
        return chrome_options

    def wait_until_page_fully_loaded(self):
        self.wait.until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )

    def switch_to_main_window(self):
        self.driver.switch_to.window(self.driver.window_handles[0])

    def fetch_url(self, url):
        try:
            self.driver.get(url)
            return True
        except WebDriverException:
            return False

    def scroll_down_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def get_links_one_level_deep(self):
        links = []
        for element in self.driver.find_elements(By.XPATH, "//a[@href]"):
            if element.is_displayed() and element.is_enabled():
                link = element.get_attribute("href")
                parsed_url = urlparse(self.driver.current_url)
                base_url = parsed_url.scheme + "://" + parsed_url.netloc
                if (
                    link is not None
                    and len(link) > 0
                    and link not in links
                    and base_url in link
                ):
                    links.append(link)
        return links

    def close_current_tab_and_switch_to_first_tab(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def open_link_in_new_tab(self, link):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get(link)
