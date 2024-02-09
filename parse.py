from bs4 import BeautifulSoup as bs
import os

results_path = 'results'

for root, dirs, files in os.walk(results_path, topdown=False):
    for name in files:
        with open(os.path.join(root, name)) as fp:
            soup = bs(fp, "html.parser")
            main = soup.body.main
            header_section = main.section
            name = header_section.h1.text

            sections = soup.body.main.find_all('section')
            # print(f'sections: \n {sections}')
            for sec in sections:
                sec_text = sec.text.strip()
                    
                if 'Experience' in sec_text:
                    experience_section = sec
                    # Check if currently in school
                    if 'Present' in experience_section.text:
                        experience_items = experience_section.find_all('li')
                        print(f'NAME: {name}\n')
                        print('-----EXPERIENCE-----')
                        for item in experience_items:
                            if 'Present' in item.text:
                                results = item.find_all("span", {"aria-hidden": "true"})
                                
                                # Remove "Skills" if found on result list
                                clean_results = [result for result in results if 'Skills' not in result.text.split(' ', 1)[0]]
                                #print(f'We got {len(clean_results)} results')
                                                                
                                # Checking if "Present" substring is in element
                                date_index_list = [idx for idx, s in enumerate(clean_results) if 'Present' in s.text]
                                if len(date_index_list) > 0:
                                    date_index = date_index_list[0]
                                    employment_data = clean_results[:date_index+1]
                                    for result in employment_data:
                                        print(result.text)
                        print('\n')
                    
                if 'Education' in sec_text:
                    education_section = sec
                    # Check if currently in school
                    if 'Present' in education_section.text:
                        education_items = education_section.find_all('li')
                        print('-----EDUCATION-----')
                        for item in education_items:
                            if 'Present' in item.text:
                                results = item.find_all("span", {"aria-hidden": "true"})
                                school = results[0].text
                                degree = results[1].text
                                print(f'school: {school} - degree: {degree}')
                        print('\n')