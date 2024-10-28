import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

load_dotenv()

def get_soup(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-agent={os.getenv('USER_AGENT')}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(), options=chrome_options)
    driver.get(url)
    html = driver.page_source
    driver.quit()

    return BeautifulSoup(html, 'html.parser')
