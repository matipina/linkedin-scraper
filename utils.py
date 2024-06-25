import time
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup as bs


def setup(headless=False, wait_time=5):
    '''
    Sets up the Selenium WebDriver for web scraping.

    This function configures and initializes a Chrome WebDriver instance with specified options.
    It can run in headless mode if desired, and sets a wait time for element loading.

    Parameters:
    headless (bool): If True, runs the WebDriver in headless mode (default is False).
    wait_time (int): The maximum amount of time (in seconds) to wait for elements to load (default is 5 seconds).

    Returns:
    tuple: A tuple containing the configured WebDriver instance and the WebDriverWait instance.
    '''
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')

    service = Service(executable_path=ChromeDriverManager().install())

    if headless:
        options.add_argument("--headless")

    driver = webdriver.Chrome(service=service, options=options)

    ignored_exceptions = (NoSuchElementException,
                          StaleElementReferenceException,)
    wait = WebDriverWait(
        driver, wait_time, ignored_exceptions=ignored_exceptions)
    return driver, wait


def parse_source_data(driver,
                      experience=True,
                      education=True,
                      current=True,
                      verbose=True):
    """
    Scrape data from a LinkedIn user's profile.

    Parameters:
    driver (webdriver): Selenium WebDriver object to control the browser.
    experience (bool): If True, scrape the user's work experience.
    education (bool): If True, scrape the user's education history.
    current (bool): If True, only scrape current work experience and education.
    verbose (bool): If True, print detailed logs of the scraping process.

    Returns:
    tuple: Two lists containing current experience and current education details.
    """

    current_experience = []
    current_education = []

    time.sleep(0.2)
    source_code = driver.page_source
    soup = bs(source_code, "html.parser")

    main = soup.body.main
    header_section = main.section
    name = header_section.h1.text
    print(f'name in parser: {name}')

    sections = soup.body.main.find_all('section')
    for sec in sections:
        sec_text = sec.text.strip()

        if experience:
            if 'Experience' in sec_text:
                experience_section = sec
                if 'Present' in experience_section.text:
                    experience_items = experience_section.find_all('li')
                    if verbose:
                        print(f'NAME: {name}\n')
                        print('-----EXPERIENCE-----')
                    for item in experience_items:
                        if 'Present' in item.text:
                            results = item.find_all(
                                "span", {"aria-hidden": "true"})

                            # Remove "Skills" if found on result list
                            try:
                                clean_results = [
                                    result for result in results if 'Skills' not in result.text.split(' ', 1)[0]]
                            except:
                                raise Exception(
                                    'Error with clean_results when parsing experience')

                            # Checking if "Present" substring is in element
                            date_index_list = [idx for idx, s in enumerate(
                                clean_results) if 'Present' in s.text]
                            if len(date_index_list) > 0:
                                date_index = date_index_list[0]
                                employment_data = clean_results[:date_index+1]
                                for result in employment_data:
                                    current_experience.append(result.text)
                                    if verbose:
                                        print(result.text)
                    if verbose:
                        print('\n')

        if education:
            if 'Education' in sec_text:
                if 'Volunteering' not in sec_text:
                    education_section = sec
                    if current:
                        # Check if currently in school
                        if 'Present' in education_section.text:
                            education_items = education_section.find_all('li')
                            if verbose:
                                print('-----EDUCATION-----')
                            for item in education_items:
                                if 'Present' in item.text:
                                    results = item.find_all(
                                        "span", {"aria-hidden": "true"})
                                    if len(results) > 1:
                                        school = results[0].text
                                        degree = results[1].text
                                        current_education.append(
                                            f'school: {school} - degree: {degree}')
                                    elif len(results) == 1:
                                        current_education.append(results[0])
                                    else:
                                        current_education.append(results)
                                    if verbose:
                                        print(
                                            f'school: {school} - degree: {degree}')
                            if verbose:
                                print('\n')
                    else:
                        # If not current, checking for latest education item
                        # In this case, current_education will actualy store the latest education
                        education_items = education_section.find_all('li')
                        latest_item = education_items[0]
                        results = latest_item.find_all(
                            "span", {"aria-hidden": "true"})
                        if len(results) > 1:
                            school = results[0].text
                            degree = results[1].text
                            current_education.append(
                                f'school: {school} - degree: {degree}')
                        elif len(results) == 1:
                            current_education.append(results[0])
                        else:
                            current_education.append(results)
                        if verbose:
                            print(f'school: {school} - degree: {degree}')

    return current_experience, current_education


def ensure_dataframe_format(df: pd.DataFrame, column_names: dict) -> pd.DataFrame:
    """
    Ensures that the DataFrame has the correct format for data scraping.

    This function performs the following checks and modifications:
    1. Checks if the DataFrame has a column named 'Name'.
       If the 'Name' column is missing, it raises a ValueError.
    2. Checks if the DataFrame has a column named 'Scraped'.
       If the 'Scraped' column is missing, it creates it and populates it with 0 for all rows.
    3. Checks if the DataFrame has a column named 'Linkedin'.
       If the 'Linkedin' column is missing, it creates it.
    4. Checks if the DataFrame has all the columns specified in the values of the `column_names` dictionary.
       If any of the required columns are missing, it raises a ValueError indicating the missing column(s).

    Parameters:
    df (pd.DataFrame): The input DataFrame that needs to be checked and formatted.
    column_names (dict): A dictionary where the values are the names of the required columns.

    Returns:
    pd.DataFrame: The DataFrame with the necessary format for scraping, including the 'Scraped' column.

    Raises:
    ValueError: If the 'Name' column does not exist in the DataFrame.
    ValueError: If any required column specified in `column_names` is missing.
    """
    # Check if 'Name' column exists
    if 'Name' not in df.columns:
        raise ValueError("The DataFrame does not have a column named 'Name'.")

    # Check if 'Scraped' column exists, if not, create it
    if 'Scraped' not in df.columns:
        df['Scraped'] = 0
        
    # Check if 'Linkedin' column exists, if not, create it
    if 'Linkedin' not in df.columns:
        df['Linkedin'] = ''

    # Check if all required columns exist
    missing_columns = [col for col in column_names.values() if col not in df.columns]
    if missing_columns:
        raise ValueError(f"The DataFrame is missing the following required column(s): {', '.join(missing_columns)}")

    return df
