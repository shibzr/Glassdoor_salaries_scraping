import pandas as pd
import numpy as np
import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import chromedriver_binary


#importing cleaning method from Cleaning
from .Cleaning import clean_rated_salaries_df

class Scrape_Data:
    """
    A class to scrape salaries data from Glassdoor through the utilisation of selenium

    Parameters:
    ----------
        city (str) : The city to search
        job (str) : The job title to search
        username (str) : The email used to login
        password (str) : The password to login

    Attributes
    ----------
        _city = storing city parameter
        _job = stroring job parameter
        _username = storing username parameter
        _password = storing password parameter
        _average_salary = storing average salary found on Glassdooor
        _prime = storing additional pay found on Glassdoor if exists
    """
    def __init__(self, username, password, city="Paris", job="Data Scientist"):
        self._city = city
        self._job = job
        self._username = username
        self._password = password
        self._average_salary = None
        self._prime = None


        #Launching the driver
        #s = Service(r"C:\Users\Shehab\Desktop\Programming\Python\Salary Negotiation\chromedriver.exe")

        #Setting options
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        #uncomment to use without installing Chromedriver
        driver = webdriver.Chrome(chrome_options=options)

        #Uncomment to use with Chromedriver alread installed
        #driver = webdriver.Chrome(chrome_options=options, service=s)

        # Navigate to Glassdoor
        driver.get("https://www.glassdoor.com")
        # Accept the cookies message
        time.sleep(10)
        cookies_button_click = driver.find_element(By.ID, "onetrust-accept-btn-handler").click()

        # Change language to English
        dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li[@class='col-9 col-sm-5 col-md-3 tldSelector']")))
        dropdown.click()
        language = driver.find_element(By.XPATH, "//*[contains(@id, 'option_22_')]")
        language.click()

        # Accept the cookies message after changing the language
        time.sleep(5)
        cookies_button_click = driver.find_element(By.ID, "onetrust-accept-btn-handler").click()

        # Login click_in:
        login = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,
                                                                                "//button[@class='d-flex align-items-center justify-content-center order-1 order-md-2 mr-auto mr-md-0 p-0 LockedHomeHeaderStyles__signInButton']")))
        driver.execute_script("arguments[0].click();", login)
        time.sleep(10)

        #Filling username
        user_name = driver.find_element(By.ID, "modalUserEmail")
        time.sleep(10)
        user_name.send_keys(self._username)
        time.sleep(10)

        #Filling password
        password = driver.find_element(By.ID, "modalUserPassword")
        password.send_keys(self._password)

        # officially_login Glassdoor
        entering_glassdoor = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
            (By.XPATH, "//button[@class='gd-ui-button mt-std minWidthBtn css-14xfqow evpplnh0']")))
        driver.execute_script("arguments[0].click();", entering_glassdoor)

        # Clicking on the salary page
        entering_salary_page = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,
                                                                                               "//div[@class='d-flex d-lg-none align-items-center justify-content-center']//a[@data-test='site-header-salaries']")))
        driver.execute_script("arguments[0].click();", entering_salary_page)

        time.sleep(3)
        # Filling post title to be searched
        job_title = driver.find_element(By.ID, "KeywordSearch")
        job_title.clear()
        job_title.send_keys(self._job)
        time.sleep(3)

        # Filling the location to be searched: by default it is the city where you are located through your IP
        location = driver.find_element(By.ID, "LocationSearch")
        location.clear()
        location.send_keys(self._city)
        time.sleep(3)

        # Clicking search button for job
        salary_search_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//button[@class='gd-btn-mkt']")))
        driver.execute_script("arguments[0].click();", salary_search_button)
        time.sleep(5)

        # Extracting average salary & average prime (additional pay) if it exists
        try:
            self._average_salary = driver.find_element(By.XPATH, "//span[@class='m-0 css-146zilq ebrouyy2']").text
            self._prime = driver.find_element(By.XPATH, "//span[@class='m-0 css-93svrw ebrouyy3']").text
        except:
            pass

        #list to hold values of each job information
        li = []

        #looping through all data pages till no more next page
        while True:
            try:
                #looping through individual salary posts
                reported_salaries = driver.find_elements(By.CSS_SELECTOR, "div[class='py css-17435dd']")
                for reported_salary in reported_salaries:
                    li.append(reported_salary.text.splitlines())
                    time.sleep(2)

                time.sleep(3)
                #Clicking on next page button if it exists
                next_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//button[@class='nextButton css-1hq9k8 e13qs2071']")))
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
            except :
                break


        #Data Cleaning
        # small companies list mostly not rated and/or startups
        # big companies list mostly salaries reporter from many employees and companies have ratings as well
        self._full_data = li

        # Exiting the driver
        driver.quit()

    def get_salaries(self, rated_companies = True, employee_status = "Full Time", junior = True):
        """
        A method to return the specified dataset based on the input of the user

        Parameters:
        ----------
            rated_companies = True
                Usually if Ture, it returns data from big companies that are rated
                if False, it returns usually data from small startups that are not rated

            employee_status : Three options
                "Full Time" | "Intern" | "Consultant"

            junior : True
                by default for junior level
                if False it means senior level jobs

            When rated_companies == False, it returns the full not rated companies dataset regardless of status and junior
        """
        #major_salaries_df for rated companies
        major_salaries_df = pd.DataFrame(data=[x for x in self._full_data if len(x) == 10 ], columns=["Rating", "Star", "Company", "Job_Title", "Annual Salary",
                                                            "Yearly/Monthly", "Based_On Count",
                                                            "How many salaries on Glassdoor", "Min Range", "Max Range"])
        #Cleaning major_salaries_df through clean_rated_salaries_df method
        major_salaries_df = clean_rated_salaries_df(major_salaries_df)
        #sorting by rating & salary
        major_salaries_df = major_salaries_df.sort_values(["Rating", "Annual Salary"], ascending=[False, False])

        #start_ups_df for usually not rated companies
        not_rated_df = pd.DataFrame(data=[x for x in self._full_data if len(x) == 8 ], columns=["Company", "Job_Title", "Approximately", "Salary", "Based_On Count",
                                                      "How many salaries on Glassdoor", "Min Range", "Max Range"])
        not_rated_df = not_rated_df.sort_values(["Rating", "Salary"], ascending=[False, False])

        if rated_companies & employee_status == "Full Time" & junior :
            #rated companies for full time junior level
            rated_full_junior_df = major_salaries_df[(major_salaries_df["Yearly/Monthly"] != "mo")
                                                     & (major_salaries_df["Job_Title"].str.contains("Monthly", case=False) == False)
                                             & (major_salaries_df["Job_Title"].str.contains("Intern", case=False) == False)
                                            & (major_salaries_df["Job_Title"].str.contains("Consultant", case=False) == False)
                                               & (major_salaries_df["Job_Title"].str.contains("Senior|Lead", case=False) == False)]
            rated_full_junior_df.reset_index(drop=True, inplace=True)
            return rated_full_junior_df

        elif rated_companies & employee_status == "Intern" & junior:
            #rated companies for intern & junior level
            rated_intern_junior_df = major_salaries_df[(major_salaries_df["Yearly/Monthly"]=="mo") | (major_salaries_df["Job_Title"].str.contains("Monthly", case=False))
                                    | (major_salaries_df["Job_Title"].str.contains("Intern", case=False))]
            rated_intern_junior_df.reset_index(drop=True, inplace=True)
            return rated_intern_junior_df

        elif rated_companies & employee_status == "Consultant" & junior:
            rated_consultant_junior = major_salaries_df[(major_salaries_df["Job_Title"].str.contains("Consultant", case=False) == True) |
                                                        (major_salaries_df["Job_Title"].str.contains("Contract",case=False) == True) &
                                                        (major_salaries_df["Job_Title"].str.contains("Senior|Lead", case=False) == False)]
            rated_consultant_junior.reset_index(drop=True, inplace=True)
            return rated_consultant_junior

        #Senior level conditions
        if rated_companies & employee_status == "Full Time" & junior==False:
            # rated companies for full time & senior level

            rated_full_senior_df = major_salaries_df[(major_salaries_df["Yearly/Monthly"] != "mo")
                                                     & (major_salaries_df["Job_Title"].str.contains("Monthly", case=False) == False)
                                             & (major_salaries_df["Job_Title"].str.contains("Intern", case=False) == False)
                                            & (major_salaries_df["Job_Title"].str.contains("Consultant", case=False) == False)
                                               & (major_salaries_df["Job_Title"].str.contains("Senior|Lead", case=False) == True)]

            rated_full_senior_df.reset_index(drop=True, inplace=True)
            return rated_full_senior_df

        elif rated_companies & employee_status == "Intern" & junior==False:

            print("There are generally no data for interns with senior level position")

        elif rated_companies & employee_status == "Consultant" & junior==False:
            # rated companies for Consultant & senior
            rated_consultant_senior = major_salaries_df[(major_salaries_df["Job_Title"].str.contains("Consultant", case=False) == True) |
                                                        (major_salaries_df["Job_Title"].str.contains("Contract",case=False) == True) &
                                                        (major_salaries_df["Job_Title"].str.contains("Senior|Lead", case=False) == True)]
            rated_consultant_senior.reset_index(drop=True, inplace=True)
            return rated_consultant_senior


        #not rated companies condition return the full dataset not cleaned regardless of status and level
        elif rated_companies == False:
            return not_rated_df