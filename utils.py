import time
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
from bs4 import BeautifulSoup as bs

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


def parse_source_data(driver, 
                      experience=True, 
                      education=True, 
                      current=True, 
                      verbose=True):
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
                # Check if currently in school
                if 'Present' in experience_section.text:
                    experience_items = experience_section.find_all('li')
                    if verbose:
                        print(f'NAME: {name}\n')
                        print('-----EXPERIENCE-----')
                    for item in experience_items:
                        if 'Present' in item.text:
                            results = item.find_all("span", {"aria-hidden": "true"})
                            
                            # Remove "Skills" if found on result list
                            try:
                                clean_results = [result for result in results if 'Skills' not in result.text.split(' ', 1)[0]]
                            except:
                                raise Exception('Error with clean_results when parsing experience') 
                                                            
                            # Checking if "Present" substring is in element
                            date_index_list = [idx for idx, s in enumerate(clean_results) if 'Present' in s.text]
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
                                    results = item.find_all("span", {"aria-hidden": "true"})
                                    if len(results) > 1:
                                        school = results[0].text
                                        degree = results[1].text
                                        current_education.append(f'school: {school} - degree: {degree}')
                                    elif len(results) == 1:
                                        current_education.append(results[0])
                                    else:
                                        current_education.append(results)
                                    if verbose:
                                        print(f'school: {school} - degree: {degree}')
                                print('OK NEXT EDU')
                            if verbose:
                                print('\n')
                    else:
                        # If not current, checking for latest education item
                        education_items = education_section.find_all('li')
                        latest_item = education_items[0]
                        results = latest_item.find_all("span", {"aria-hidden": "true"})
                        if len(results) > 1:
                            school = results[0].text
                            degree = results[1].text
                            current_education.append(f'school: {school} - degree: {degree}')
                        elif len(results) == 1:
                            current_education.append(results[0])
                        else:
                            current_education.append(results)
                        if verbose:
                            print(f'school: {school} - degree: {degree}')
                        
    return current_experience, current_education
