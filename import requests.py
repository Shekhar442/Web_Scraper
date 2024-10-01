# Extract all the <h1> headers and <a> tags from the page using Beautifulsoup

import requests
from bs4 import BeautifulSoup

# URL of the website you want to scrape
url = 'https://Shail-shri.com'

# Send a GET request to the website
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Example: Extract all the <h1> headers from the page
    headers = soup.find_all('h1')
    
    # Print the headers text
    for header in headers:
        print(header.text)
else:
    print(f"Failed to retrieve data from {url}, Status Code: {response.status_code}")

# Extract all the <a> tags that represent hyperlinks
soup = BeautifulSoup(response.content, 'html.parser')
links = soup.find_all('a')

# Loop through all <a> tags and print the URLs
for link in links:
    href = link.get('href')
    if href:
        print(href)
