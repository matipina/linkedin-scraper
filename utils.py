from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def setup(headless=False, wait_time=5):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')

    service = Service(executable_path=ChromeDriverManager().install())

    if headless:
        options.add_argument("--headless")

    driver = webdriver.Chrome(service=service, options=options)

    ignored_exceptions=(NoSuchElementException, StaleElementReferenceException,)
    wait = WebDriverWait(driver, wait_time, ignored_exceptions=ignored_exceptions)
    return driver, wait
