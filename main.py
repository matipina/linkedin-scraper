from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup as bs
import re as re
import time
import datetime
import pandas as pd
from utils import setup, parse_source_data, ensure_dataframe_format
from dotenv import load_dotenv
import os
import sys
import random


load_dotenv()
CREDENTIALS = {
    'username': os.environ["LINKEDIN_USERNAME"],
    'password': os.environ["LINKEDIN_PASSWORD"]
}

URL_LOGIN = "https://www.linkedin.com/uas/login"
URL_PUBLIC = "https://www.linkedin.com/"

filters = ["The New School", "Parsons School of Design"]

def login(driver, wait, credentials):
    """
    Handle login to LinkedIn account.

    Parameters:
    driver (webdriver): Selenium WebDriver object to control the browser.
    wait (WebDriverWait): WebDriverWait object to manage waits.
    credentials (dict): Dictionary containing 'username' and 'password' for login.

    Returns:
    None
    """
    try:
        # Wait for the email field and enter the username
        wait.until(EC.presence_of_element_located((By.ID, "username")))
        email_field = driver.find_element(By.ID, "username")
        email_field.send_keys(credentials["username"])

        # Wait for the password field and enter the password
        wait.until(EC.presence_of_element_located((By.ID, "password")))
        pass_field = driver.find_element(By.ID, "password")
        pass_field.send_keys(credentials["password"])

        # Adding a short delay to mimic human interaction
        time.sleep(random.uniform(0.7, 1.4))

        # Wait for the sign-in button and click it
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="organic-div"]/form/div[3]/button'))).click()

        # Adding a short delay to ensure the login process completes
        time.sleep(0.5)

        print('Login successful.')

    except Exception as e:
        print(f"An error occurred during login: {e}")


def search_item(name,
                users,
                driver,
                wait,
                column_names=None,
                verbose=True,
                download=True):
    '''
    Function to search and scrape from LinkedIn a specific user profile 
    based on their name
    '''
    linkedin_column = column_names['linkedin']
    status_column = column_names['status']
    employer_column = column_names['employer']
    position_column = column_names['position']
    education_column = column_names['education']

    if verbose:
        print(f'searching for user: {name}')
    wait.until(EC.url_contains('https://www.linkedin.com/'))

    # Search bar
    search_bar = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="global-nav-typeahead"]/input')))
    search_bar.click()

    # Clean search bar
    search_bar.send_keys(Keys.COMMAND + "a")
    search_bar.send_keys(Keys.DELETE)
    time.sleep(0.2)

    # Input user
    search_bar.send_keys(name)

    # Submit and wait for results
    search_bar.send_keys(Keys.ENTER)
    time.sleep(0.3)

    wait.until(EC.url_contains('https://www.linkedin.com/search/results/'))
    time.sleep(0.8)

    users_not_found = driver.find_elements(
        By.XPATH, '//h2[normalize-space()="No results found"]')

    # If no results, skip
    if len(users_not_found) != 0:
        if verbose:
            print(f'No results in initial user search!')
            print('Assigned scraped = 2')
        users.loc[users['Name']
                  == name, linkedin_column] = 'Not Found'
        users.loc[users['Name'] == name, 'Scraped'] = 2
        # driver.get('https://www.linkedin.com/feed/')
        return

    # Check if we're already filtering by people by checking the URL. If not, do it
    if "results/people/" in driver.current_url:
        print("We're already filtering by people!")
    else:
        # Filter by people
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//button[normalize-space()="People"]'))).click()
        print("Filtered by people now.")

    time.sleep(0.1)

    # If any results, add filters by school

    # Check if we have results.
    users_not_found = driver.find_elements(
        By.XPATH, '//h2[normalize-space()="No results found"]')
    if len(users_not_found) == 0:
        # All filters
        time.sleep(0.5)
        wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             '//button[normalize-space()="All filters"]'))).click()

        time.sleep(0.2)

        # Check if the current URL contains the string "schoolFilter="
        if "schoolFilter=" in driver.current_url:
            if verbose:
                print("The current URL contains 'schoolFilter='.")
        else:            
            for filter in filters:
                if verbose:
                    print(f'adding {filter} filter')
                time.sleep(0.2)
                # Add a school
                wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//button[normalize-space()="Add a school"]'
                    ))).click()
                time.sleep(0.3)

                # Write each school name
                add_school_input = driver.switch_to.active_element
                add_school_input.click()
                add_school_input.send_keys(filter)
                time.sleep(random.uniform(0.2, 0.6))
                add_school_input.click()
                time.sleep(0.3)
                add_school_input.send_keys(Keys.ARROW_DOWN)
                add_school_input.send_keys(Keys.RETURN)
                time.sleep(random.uniform(0.2, 0.6))

        # Show Results
        wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             '//button[normalize-space()="Show results"]'))).click()
        random.uniform(0.2, 0.6)

        # Get all results

        # Check if we have results. If we do:
        not_found = driver.find_elements(
            By.XPATH, '//h2[normalize-space()="No results found"]')
        if len(not_found) == 0:
            try:
                if verbose:
                    print('looking for results...')
                time.sleep(0.5)
                results = wait.until(EC.element_to_be_clickable((
                    By.CLASS_NAME, 'search-results-container'
                )))
                time.sleep(0.1)
                found = results.find_elements(
                    By.CLASS_NAME, 'reusable-search__result-container')
                # found = results.find_elements(By.CLASS_NAME, 'entity-result')
                if verbose:
                    print(f'found: {len(found)} entries!')
                count = 0
                if len(found) > 0:
                    for result in found:
                        if 'LinkedIn Member' not in result.text:
                            result_link = result.find_elements(By.TAG_NAME, 'a')[
                                0].get_attribute('href')
                            driver.execute_script(
                                f"window.open('{result_link}', 'tab2');")
                            time.sleep(random.uniform(0.1, 0.3))
                            driver.switch_to.window("tab2")

                            wait.until(EC.url_contains(
                                'https://www.linkedin.com/in/'))

                            time.sleep(random.uniform(0.4, 0.6))
                            # Wait until "Education" section is loaded
                            try:
                                wait.until(EC.presence_of_element_located(
                                    (By.ID, "education")))
                            except Exception as e:
                                print(
                                    f"Couldn't find education. Exception: {e}")
                            time.sleep(0.2)

                            current_experience, current_education = parse_source_data(
                                driver=driver,
                                experience=False,
                                education=True,
                                current=False,
                                verbose=True)

                            if verbose:
                                print('Finished parsing!')

                            # Download user profile if selected
                            if download:
                                path = 'education_results'
                                download_profile(f'{name}', driver, path)

                            # Add linkedin link
                            users.loc[users['Name'] == name,
                                          linkedin_column] = driver.current_url
                            if verbose:
                                print(f'Added this link: {driver.current_url}')

                            if len(current_experience) > 0:
                                status = 'Employed'
                            elif len(current_education) > 0:
                                status = 'Enrolled/Accepted in further education'
                            else:
                                status = 'No data'

                            users.loc[users['Name'] ==
                                      name, status_column] = status
                            users.loc[users['Name'] == name,
                                      employer_column] = ' '.join(str(x) for x in current_experience)
                            users.loc[users['Name'] == name, position_column] = ' '.join(
                                str(x) for x in current_experience)
                            users.loc[users['Name'] == name, education_column] = ' '.join(
                                str(x) for x in current_education)

                            users.loc[users['Name']
                                      == name, 'Scraped'] = 1
                            if verbose:
                                print('assigned scraped = 1')

                            time.sleep(0.1)
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            count += 1

                            if count >= 1:
                                break
                        else:
                            if verbose:
                                print('No results in search!')
                                print('Assigned scraped = 2')
                            users.loc[users['Name']
                                      == name, 'Scraped'] = 2
                            users.loc[users['Name'] == name,
                                      linkedin_column] = 'Not Found'
                            break
                else:
                    if verbose:
                        print('No results in search!')
                        print('Assigned scraped = 2')
                    users.loc[users['Name']
                              == name, 'Scraped'] = 2
                    users.loc[users['Name'] == name,
                              linkedin_column] = 'Not Found'
                    time.sleep(random.uniform(0, 1))
            except Exception as e:
                if verbose:
                    print(f"Error while looking for {name}:")
                    print(e)
                    print('Assigned scraped = -1')
                users.loc[users['Name'] == name,
                          linkedin_column] = 'Not Found'
                users.loc[users['Name']
                          == name, 'Scraped'] = -1
                driver.get('https://www.linkedin.com/feed/')
        else:
            if verbose:
                print(f'No results in refined search!')
                print('Assigned scraped = 2')
            users.loc[users['Name'] == name,
                      linkedin_column] = 'Not Found'
            users.loc[users['Name'] == name, 'Scraped'] = 2

        return
    else:
        if verbose:
            print('No results in general search!')
            print('Assigned scraped = 2')
        users.loc[users['Name'] == name, 'Scraped'] = 2
        users.loc[users['Name'] == name,
                  'ALL SOURCES: LinkedIn Profile Links'] = 'Not Found'
        driver.get('https://www.linkedin.com/feed/')


def download_profile(user, driver, path):
    print(f'download profile {user}')
    page_contents = driver.page_source

    soup = bs(page_contents, "html.parser")
    name = soup.body.main.section.h1.text.lower()
    usernames = user.lower().strip("_0123456789").split()
    names = name.split()

    if any(x in usernames for x in names):
        with open(f"{path}/{name}({user}).html", "w", encoding='utf-8') as f:
            f.write(page_contents)
            print('saving file...')


def search_public_people(users, wait):
    '''
    '''

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


def scrape_data(
    users,
    headless,
    verbose,
    attempts,
    path,
    user_login=True,
    column_names=None
):
    """
    Scrape data for a list of names from LinkedIn.

    Parameters:
    users (df): Dataframe of users to search and scrape data.
    headless (bool): Run the browser in headless mode if True.
    verbose (bool): Print detailed logs if True.
    attempts (int): Number of attempts to retry in case of failure.
    path (str): Path to save the scraped data.
    user_login (bool): If True, login to LinkedIn before scraping.

    Returns:
    None
    """

    driver, wait = setup(headless=headless, wait_time=6)
    names = users['Name']

    if user_login:
        driver.get(URL_LOGIN)
        wait.until(EC.url_to_be(URL_LOGIN))
        login(driver=driver, wait=wait, credentials=CREDENTIALS)
        time.sleep(0.3)
        print('log in sucessful!')

        total_scraped = 0
        for name in names:
            if total_scraped >= 300:
                break
            try:
                search_item(
                    name=name,
                    users=users,
                    driver=driver,
                    wait=wait,
                    column_names=column_names,
                    verbose=verbose,
                    download=False
                )
                # users.loc[users['Name'] == name, 'Scraped'] = 1
            except Exception as e:
                print(f'Exception on user {name}: \n{e}\n')
                users.loc[users['Name']
                          == name, 'Scraped'] = -1

                if verbose:
                    print(f'Skipping to next user...')
                time.sleep(0.2)
            users.to_excel(path, index=False)
            total_scraped += 1

    else:
        driver.get(URL_PUBLIC)
        wait.until(EC.url_to_be(URL_PUBLIC))
        time.sleep(0.3)
        search_public_people(names, driver, wait)


def main(users,
         path,
         headless=True,
         verbose=False,
         attempts=3,
         column_names=None):

    if verbose:
        print(f'Running scraper on headless: {
              headless} mode. Verbose: {verbose}')

    scrape_data(
        users=users,
        headless=headless,
        verbose=verbose,
        attempts=attempts,
        path=path,
        user_login=True,
        column_names=column_names
    )


if __name__ == "__main__":
    headless = False
    verbose = False
    path = 'data/2024/data_updated.xlsx'
    selection = 'ALL SOURCES: Primary Status'

    '''
    First argument: headless
    Second argument: verbose
    Third argument: path to the file containing the data to scrape
    Forth argument: column to filter by
    '''
    if len(sys.argv) >= 2:  # At least one argument
        headless = (sys.argv[1].lower() in ("1", "True", "headless"))
        if len(sys.argv) >= 3:  # At least two arguments
            verbose = (sys.argv[2] in ("1", "True", "verbose"))
            if len(sys.argv) >= 4:  # At least three arguments
                path = sys.argv[3]
                if len(sys.argv) >= 5:  # At least three arguments
                    selection = sys.argv[4]

    user_data = pd.read_excel(path)

    # Reverse rows using iloc() Function
    # user_data = user_data.iloc[::-1]
    user_data = user_data.copy()

    # Dictionary with the names of the columns that are needed in the scraping process
    column_names = {
        'linkedin': 'Linkedin',
        'status': 'ALL SOURCES: Primary Status',
        'employer': 'ALL SOURCES: Employer/Organization Name',
        'position': 'ALL SOURCES: Position Title',
        'education': 'ALL SOURCES: Further Educ_ Institutions'
    }

    # Make sure that input file format is right
    user_data = ensure_dataframe_format(
        df=user_data, column_names=column_names)

    # Select users that have a missing primary status
    selected_users = user_data[user_data[selection].isnull()]

    # Select users that have not been previously scraped yet
    selected_users = selected_users[~selected_users['Scraped'].isin([1, 2])]

    main(
        users=selected_users,
        path=path,
        headless=headless,
        verbose=verbose,
        column_names=column_names
    )
