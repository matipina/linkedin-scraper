from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import re as re
import time
import pandas as pd
from utils import setup
from dotenv import load_dotenv
import os
import sys
import traceback


load_dotenv()
CREDENTIALS = {
    'username': os.environ["LINKEDIN_USERNAME"],
    'password': os.environ["LINKEDIN_PASSWORD"]
}

URL_LOGIN = "https://www.linkedin.com/uas/login"
URL_PUBLIC = "https://www.linkedin.com/"


def login(driver, wait, credentials):
    '''
    Function to handle login to LinkedIn accont
    '''
    # Email field
    wait.until(EC.presence_of_element_located((By.ID, "username")))
    email_field = driver.find_element(By.ID, "username")
    email_field.send_keys(credentials["username"])

    # Password field
    wait.until(EC.presence_of_element_located((By.ID, "password")))
    pass_field = driver.find_element(By.ID, "password")
    pass_field.send_keys(credentials["password"])

    # Sign up button
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="organic-div"]/form/div[3]/button'))).click()


def search_item(user, driver, wait):
    '''
    Function to search for a specific item
    '''
    print(f'user: {user}')
    wait.until(EC.url_to_be('https://www.linkedin.com/feed/'))

    # Search bar
    search_bar = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="global-nav-typeahead"]/input')))
    search_bar.click()

    # Input user
    search_bar.send_keys(user)

    # Submit and wait for results
    search_bar.send_keys(Keys.ENTER)
    time.sleep(0.3)

    wait.until(EC.url_contains('https://www.linkedin.com/search/results/'))
    time.sleep(0.3)

    # See all results for people
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//button[normalize-space()="People"]'
         ))).click()

    time.sleep(0.2)

    # If any results, add filters by school

    # Check if we have results.
    users_not_found = driver.find_elements(
        By.XPATH, '//h2[normalize-space()="No results found"]')
    if len(users_not_found) == 0:
        # All filters
        wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             '//button[normalize-space()="All filters"]'))).click()

        time.sleep(0.2)
        filters = ["The New School", "Parsons School of Design",
                   "The New School's Milano School"]
        for filter in filters:
            print(f'adding {filter} filter')
            time.sleep(0.1)
            # Add a school
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[normalize-space()="Add a school"]'
                 ))).click()
            time.sleep(0.2)

            # Write each school name
            add_school_input = driver.switch_to.active_element
            add_school_input.click()
            add_school_input.send_keys(filter)
            time.sleep(0.5)
            add_school_input.click()
            add_school_input.send_keys(Keys.ARROW_DOWN)
            add_school_input.send_keys(Keys.RETURN)
            time.sleep(0.5)

        # Show Results
        wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             '//button[normalize-space()="Show results"]'))).click()
        time.sleep(0.3)

        # Get all results

        # Check if we have results. If we do:
        not_found = driver.find_elements(
            By.XPATH, '//h2[normalize-space()="No results found"]')
        if len(not_found) == 0:
            try:
                print('looking for results...')

                results = wait.until(EC.element_to_be_clickable((
                    By.CLASS_NAME, 'scaffold-layout__main'
                )))
                found = results.find_elements(By.CLASS_NAME, 'entity-result')
                print(f'found: {len(found)} entries!')
                count = 0
                for result in found:
                    result_link = result.find_elements(By.TAG_NAME, 'a')[
                        0].get_attribute('href')
                    driver.execute_script(
                        f"window.open('{result_link}', 'tab2');")
                    time.sleep(0.1)
                    driver.switch_to.window("tab2")
                    download_profile(f'{user}_{count}', driver, wait)
                    time.sleep(0.1)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    count += 1

                    if count > 4:
                        break

                driver.get('https://www.linkedin.com/feed/')
            except Exception as e:
                print(f"Couldn't find {user}")
                print(e)
        else:
            print(f'No results in second search!')
            driver.get('https://www.linkedin.com/feed/')
        return
    else:
        print('No results in first search!')
        driver.get('https://www.linkedin.com/feed/')


def read_source_data(driver, wait):
    source_code = driver.page_source
    soup = bs(source_code, "html.parser")
    print(f'title: \n{soup.head.title}')

    print(f'main: \n {soup.body.main}')
    print(f'all mains: \n {soup.find_all("main")}')


def download_profile(user, driver, wait):
    print(f'download profile {user}')
    wait.until(EC.url_contains('https://www.linkedin.com/in/'))
    page_contents = driver.page_source

    soup = bs(page_contents, "html.parser")
    name = soup.body.main.section.h1.text.lower()
    usernames = user.lower().strip("_0123456789").split()
    names = name.split()

    print(f'comparing \n{names}\n with \n{usernames}')
    if any(x in usernames for x in names):
        with open(f"results/{name}.html", "w", encoding='utf-8') as f:
            f.write(page_contents)
            print('saving file...')


def search_public_people(users, driver, wait):
    # People button
    wait.until(EC.element_to_be_clickable(
        (By.PARTIAL_LINK_TEXT, 'People'))).click()
    time.sleep(0.3)

    for user in users:
        # First name field
        first_name = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="people-search-panel"]/form/section[1]/input')))
        first_name.send_keys(user['first_name'])
        # Last name field
        last_name = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="people-search-panel"]/form/section[2]/input')))
        last_name.send_keys(user['last_name'])

        time.sleep(0.3)
    return


def scrape_data(users, headless, verbose, attempts, user_login=True):
    driver, wait = setup(headless=headless, wait_time=10)

    if user_login:
        driver.get(URL_LOGIN)
        wait.until(EC.url_to_be(URL_LOGIN))
        login(driver=driver, wait=wait, credentials=CREDENTIALS)
        time.sleep(0.3)

        for user in users:
            search_item(user=user, driver=driver, wait=wait)
    else:
        driver.get(URL_PUBLIC)
        wait.until(EC.url_to_be(URL_PUBLIC))
        time.sleep(0.3)
        search_public_people(users, driver, wait)


def main(users,
         headless=True,
         verbose=False,
         attempts=3):

    print(f'Running scraper on headless: {headless} mode. Verbose: {verbose}')
    names = users['Name']
    scrape_data(names, headless, verbose, attempts, user_login=True)


if __name__ == "__main__":
    headless = False
    verbose = False

    user_data = pd.read_excel('data/Class2022.xlsx',
                              usecols=['Name', 'Major', 'Primary College', 'ALL SOURCES: Primary Status'])

    selected_users = user_data[user_data['ALL SOURCES: Primary Status'].isnull(
    )]
    print(selected_users.info())
    test_users = user_data.sample(5)

    if len(sys.argv) >= 2:  # At least one argument
        headless = (sys.argv[1].lower() in ("1", "True", "headless"))
        if len(sys.argv) > 2:  # At least two arguments
            verbose = (sys.argv[-1] in ("1", "True", "verbose"))

    main(test_users,
         headless=headless,
         verbose=verbose)
