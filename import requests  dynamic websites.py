from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Path to your WebDriver (e.g., ChromeDriver)
# driver_path = "path/to/chromedriver"
driver_path = "C://Users//Shekhar//Desktop//Web_Scraper//chromedriver.exe"

# Create a Service object
service = Service(driver_path)

# Initialize the WebDriver with the service 
driver = webdriver.Chrome(service=service)

# Navigate to the desired URL
driver.get('https://sites.google.com/view/shekhar-portfolio/')

# Extract page source after JavaScript has rendered the content
page_source = driver.page_source

# Use BeautifulSoup to parse the dynamic content
from bs4 import BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Example: Extract all the <p> elements
paragraphs = soup.find_all('p')
for paragraph in paragraphs:
    print(paragraph.text)

# Close the browser when done
driver.quit()