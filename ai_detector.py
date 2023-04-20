from base_scraper import BaseScraper
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
##from selenium import webdriver
from selenium.webdriver.common.by import By
import re

class AIDetector(BaseScraper):
    def __init__(self):
        super().__init__()
        self.driver.get("https://zerogpt.com/")
    def get_AI_percentage(self, text):
        text_area = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="textArea"]')))
        text_area.send_keys(text)
        submit_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'scoreButton')))
        self.scroll_down_to_bottom()
        submit_button.click()
        ai_percentage = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[1]/div[3]/div/div/div[1]/span')))
        return self.extract_percentage_number(ai_percentage.text)
    
    def extract_percentage_number(self, text):
        match = re.search(r"(\d+\.\d+)%", text)
        number = float(match.group(1))
        return int(number)