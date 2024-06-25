# LinkedIn Alumni Scraper

A LinkedIn webscraper written in Python that allows to gather information about The New School alumni.
To use it, it's neccesary to employ an already existing LinkedIn Account.

## Overview

This tool uses an user's personal LinkedIn credentials to automate the process of looking for former students at The New School, with the objective of gathering insights on the career paths of a large number of alumni.

Using an Excel file (.xlsx) as input, the script looks for each individual, one at a time, using LinkedIn's search bar. If a use is found, the tool opens their profile in a separate tab, to then gather the information corresponding to their most recent education and work experiences. This information gets stored in the same initial file.

## Setup

### Requirements

Before you start, make sure you have the following elements available:

* A LinkedIn account
* Google Chrome
* Python 3+ (The current version has been tested using Python 3.12)
* An Excel file to use as input and output

Start by cloning this repository with the following commands:

```zsh
git clone https://github.com/matipina/linkedin-scraper.git
cd linkedin-scraper
```

Now, install the required libraries running the following command:

`pip3 install -r requirements.txt`

To allow the script to login into your LinkedIn account, you'll need to store your credentials using a `.env` file. To generate this, run the following command:

`cp .env.example .env`

This will generate a file to store your credentials as environment variables. You can now open this file and store your username and password in the indicated fields.

## How to use

### Input file

The files to be used as input need to be a .xlsx file, which will contain the information of the users that will be searched.
The file can have any number of columns and rows, but the following column headers need to be present:

* Name: Contains the full name of each user. If the original file has the users' names separated in two or more columns, it will be necessary to join them beforehand.

### Running the script

To run the script, open the terminal and copy the following command:

```bash
python3 main.py [headless] [verbose] [data_path] [filter_column]
```

#### Arguments

1. **headless** (optional): Set this argument to `1`, `True`, or `headless` to run the script in headless mode.
2. **verbose** (optional): Set this argument to `1`, `True`, or `verbose` to enable verbose logging.
3. **data_path** (optional): The path to the Excel file containing the data to scrape.
4. **filter_column** (optional): The name of the column to filter by.

### Default Values

If no arguments are provided, the script uses the following default values:

* `headless`: `False`
* `verbose`: `False`
* `data_path`: `'data/2024/CLASS2023_merged.xlsx'`
* `filter_column`: `'ALL SOURCES: Primary Status'`

### Example Usage

Here are some example commands to run the script:

1. **Run with default values:**

   ```bash
   python3 main.py
   ```

2. **Run in headless mode:**

   ```bash
   python3 main.py headless
   ```

3. **Run with verbose logging:**

   ```bash
   python3 main.py False verbose
   ```

4. **Run with a specific data file and filter column:**

   ```bash
   python3 main.py False False data/2024/CLASS2023_merged.xlsx 'Primary Status'
   ```

### Column Names

The script uses a dictionary called `column_names` to map the necessary column names for the scraping process. These column names can be modified depending on the names of the columns in your input file. The default column names used are:

* **LinkedIn Profile Links**: `Linkedin`
* **Primary Status**: `What best describes your primary status?`
* **Employer/Organization Name**: `Please provide the following details about your job. - Employer/Organization Name`
* **Position Title**: `Please provide the following details about your job. - Position Title`
* **Educational Institution**: `Which institution/college/university you are currently enrolled at?`

You can adjust these names in the `column_names` dictionary according to the specific column names in your input file.

### Script Workflow

1. **Argument Parsing:**
   The script first parses the command-line arguments and sets the appropriate values for `headless`, `verbose`, `data_path`, and `filter_column`.

2. **Load Data:**
   The script loads the data from the specified Excel file into a pandas DataFrame.

3. **Data Formatting:**
   The `ensure_dataframe_format` function checks and formats the DataFrame to ensure it has the required columns. If any required column is missing, the function raises an error indicating the missing column name.

4. **Filter Data:**
   The script selects the rows that have not been previously scraped by checking the `Scraped` column.

5. **Run Main Function:**
   The `main` function is called with the selected users, file path, headless and verbose settings, and the column names dictionary.

By following these instructions, you can run the script with different configurations and ensure that your data is correctly processed for scraping. Adjust the `column_names` dictionary as needed to match the specific structure of your input file.

### Output

The output will be stored in the input fi

## Notes

In case there's conflict with python versions from external apps (i.e. Touchdesigner), run:

`unset PYTHONPATH`

## Disclaimers

Due to possible the presence of captchas, this program cannot run completely unsupervised. It requires human input everytime that a captcha pops up.
