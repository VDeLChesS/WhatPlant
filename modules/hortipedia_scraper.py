from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
# from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests

# Set up the Chrome WebDriver using WebDriver Manager
# options = webdriver.ChromeOptions()
# options.add_argument("--headless") # Set to "--headless" if you want headless browsing
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the target URL
url = 'https://de.hortipedia.com/Kategorie_Familia'
response = requests.get(url)
# driver.get(url)
print(response.text)



# Function to scrape the Family names on the current page
def scrape_family_names(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    family_elements = soup.find_all('span', {'ng-bind-html': 'item.title', 'class': 'ng-binding'})
    families = [family.text.strip() for family in family_elements]
    return families

# Function to scrape the Genus names after clicking on a Family name
def scrape_genus_names(family_name):
    url_genus = 'https://de.hortipedia.com/Kategorie_' + family_name
    soup = BeautifulSoup(url_genus, 'html.parser')
    genus_elements = soup.find_all('span', {'ng-bind-html': 'item.title', 'class': 'ng-binding'})
    genera = [genus.text.strip() for genus in genus_elements]
    return genera

# Function to scrape species for a genus
def scrape_species():
    try:
        species_list = []
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        species_elements = soup.find_all('span', {'ng-bind-html': 'item.title', 'class': 'ng-binding'})
        species_list = [species.text.strip() for species in species_elements]
        return species_list
    except Exception as e:
        print(f"Error scraping species: {e}")
        return []





'''
# Initialize empty DataFrames to store Family and Genus data
family_df = pd.DataFrame(columns=['ID', 'Family Name'])
genus_df = pd.DataFrame(columns=['ID', 'Family ID', 'Genus Type Name', 'Species'])

family_id = 0 # Primary Key counter for Families
genus_id = 0 # Primary Key counter for Genus

# Scrape Family names and associated Genus names across all pages
while True:
    # Scrape the current page's family names
    family_names = scrape_family_names(driver.page_source)

    # Check if family names are found, if not, exit
    if not family_names:
        print("No family names found on this page.")
        break

    # Loop through each Family name and click to get Genus names
    for family in family_names:
        family_id += 1
        # Add family to the family DataFrame
        family_df = family_df.append({'ID': family_id, 'Family Name': family}, ignore_index=True)

        # Find and click on the family name link
        try:
            family_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//span[text()='{family}']"))
            )
            ActionChains(driver).move_to_element(family_element).click().perform()
            time.sleep(2) # Wait for the page to load

            # Scrape the Genus names for this family
            genus_names = scrape_genus_names()

            # Loop through each Genus and click to scrape species
            for genus in genus_names:
                genus_id += 1

                # Add Genus to the Genus DataFrame
                genus_df = genus_df.append({'ID': genus_id, 'Family ID': family_id, 'Genus Type Name': genus, 'Species': ''}, ignore_index=True)

                # Click on the genus to load species (if any)
                genus_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//span[text()='{genus}']"))
                )
                ActionChains(driver).move_to_element(genus_element).click().perform()
                time.sleep(2) # Wait for the page to load

# Scrape species
                species_list = scrape_species()
                if species_list:
                    genus_df.loc[genus_df['ID'] == genus_id, 'Species'] = ', '.join(species_list)

                # Go back to the Genus list page
                driver.back()
                time.sleep(2) # Wait for the page to load

        except Exception as e:
            print(f"Error while processing family {family}: {e}")
            continue

        # Go back to the Family list page
        driver.back()
        time.sleep(2) # Wait for the page to load back

    # Find the "Next Page" button and click it, if available
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@ng-click='navigateSubcategories(sStartId+100)']"))
        )
        next_button.click()
        time.sleep(3) # Wait for the next page to load
    except Exception as e:
        print("Reached the last page or encountered an error:", e)
        break # Exit the loop if no more pages or an error occurs

# Print the Family and Genus Tables
print("\nFamily Table:")
print(family_df)

print("\nGenus Table:")
print(genus_df)

# Save the tables as CSV files
family_df.to_csv('family_table.csv', index=False)
genus_df.to_csv('genus_table.csv', index=False)

print("Scraping complete. Data saved to 'family_table.csv' and 'genus_table.csv'.")

# Close the browser
driver.quit()
'''