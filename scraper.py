import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

load_dotenv()

def get_soup(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument(f"user-agent={os.getenv('USER_AGENT')}")
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--log-level=3")  # Fatal log level

    driver = webdriver.Chrome(service=ChromeService(), options=chrome_options)
    driver.get(url)
    html = driver.page_source
    driver.quit()

    return BeautifulSoup(html, 'html.parser')
