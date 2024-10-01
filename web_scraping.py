import requests
from bs4 import BeautifulSoup
import json
import os

# URL of the website you want to scrape
url = 'https://Shail-shri.com'
output_dir = 'output_files'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Send a GET request to the website
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract all the <h1> headers from the page
    headers = [header.text for header in soup.find_all('h1')]
    
    # Extract all the <a> tags that represent hyperlinks
    links = [link.get('href') for link in soup.find_all('a') if link.get('href')]

    # Output to .txt
    with open(os.path.join(output_dir, 'output.txt'), 'w') as f:
        f.write('Headers:\n')
        f.write('\n'.join(headers))
        f.write('\n\nLinks:\n')
        f.write('\n'.join(links))

    # Output to .html
    with open(os.path.join(output_dir, 'output.html'), 'w') as f:
        f.write('<html><body>')
        f.write('<h1>Headers</h1><ul>')
        for header in headers:
            f.write(f'<li>{header}</li>')
        f.write('</ul><h1>Links</h1><ul>')
        for link in links:
            f.write(f'<li><a href="{link}">{link}</a></li>')
        f.write('</ul></body></html>')

    # Output to .json
    with open(os.path.join(output_dir, 'output.json'), 'w') as f:
        json.dump({'headers': headers, 'links': links}, f, indent=4)

else:
    print(f"Failed to retrieve data from {url}, Status Code: {response.status_code}")