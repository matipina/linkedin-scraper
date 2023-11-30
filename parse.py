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
            print(f'{name}')
            
            sections = soup.body.main.find_all('section')
            for sec in sections:
                print(f'section: {sec.text.strip()}')