from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
import sys
import time
import socket

class WikiInfoBox(object):

    def __init__(self, url):
        socket.setdefaulttimeout(30)
        self.ua_generator = UserAgent()
        self.url = url

        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--incognito")
        self.options.add_argument(f'user-agent={self.ua_generator.chrome}')

        self.driver = webdriver.Chrome('resources/chromedriver', options=self.options)

        self.driver.get(self.url)

        self.label_elements = ""
        self.value_elements = ""
        self.labels = []
        self.values = []

    def get_infobox(self):

        self.label_elements = self.driver.find_elements(By.CLASS_NAME,'infobox-label')
        time.sleep(1)
        self.value_elements = self.driver.find_elements(By.CLASS_NAME, 'infobox-data')
        time.sleep(1)
        dict = {}
        if not self.label_elements or not self.value_elements:
            self.label_elements = self.driver.find_elements(By.XPATH, '//td/table/tbody/tr/th')
            self.value_elements = self.driver.find_elements(By.XPATH, '//td/table/tbody/tr/td')

        for l, v in zip(self.label_elements, self.value_elements):
            dict[l.text] = v.text

        return dict


if __name__ == '__main__':
    s = WikiInfoBox(url='https://en.wikipedia.org/wiki/World_War_II')
    ib = s.get_infobox()
    if not ib:
        print("empty")
    else:
        print(ib)



