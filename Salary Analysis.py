from Glassdoor import Scrape_Data


data_scientist = Scrape_Data(city="Paris", job="Data Scientist", username="fill_yours_here", password="fill_yours_here")

#Example: Extracting dataframe of junior data scientis' salaries

df = data_scientist.get_salaries(rated_companies = True, employee_status = "Full Time", junior = True)

