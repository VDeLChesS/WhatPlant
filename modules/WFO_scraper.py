'''
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
import urllib3
import html5lib
import lxml
import lxml.html
from html.parser import HTMLParser

# Set up the Chrome WebDriver using WebDriver Manager
# options = webdriver.ChromeOptions()
# options.add_argument("--headless") # Set to "--headless" if you want headless browsing
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# url = 'https://worldfloraonline.org/classification'
# reponse = requests.get(url, verify=False)
# print(reponse.text)
# driver.get(url)

# print(response.status_code)

# Function to scrape the Family names on the current page
def scrape_order_names():
    url = 'https://worldfloraonline.org/classification'
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html5lib')
    categories = soup.find('div', class_='jstree-default jstree jstree-0 jstree-focused')
    order_elements = categories.find_all('li', class_='jstree-closed')
    orders = [order_element.find('a').find('ins').text for order_element in order_elements]
    return orders


#plant_orders = scrape_order_names()
#print(plant_orders)

url = 'https://worldfloraonline.org/classification'
response = requests.get(url, verify=False)
soup = BeautifulSoup(response.text, 'html5lib')
# print(soup.prettify())
categories = soup.find_all('ul')
for category in categories:
    print(category.text)
# a = soup.find('ul', class_='jstree jstree jstree-focused')
# print(a.text)
'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def scrape_order_names():
    url = 'https://worldfloraonline.org/classification'

    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU

    # Initialize the Selenium WebDriver (ensure you have chromedriver in your PATH)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Get the rendered page source after JavaScript is loaded
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all the elements that contain the order names
    categories = soup.find_all('li', class_='jstree-closed')

    # Extract the text (order names) from the elements
    orders = [category.find('a').text.strip() for category in categories]

    # Close the browser after scraping
    driver.quit()
    return orders


plant_orders = scrape_order_names()
print(plant_orders)