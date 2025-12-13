# 🌐 Web Scraper with Selenium

A modern, user-friendly web scraping application built with Streamlit and Selenium. This tool allows you to scrape dynamic websites that require JavaScript rendering, extract various types of content, and export the results in multiple formats.

## ✨ Features

- **🌐 Dynamic Web Scraping**: Uses Selenium to handle JavaScript-rendered content
- **📊 Multiple Scraping Options**:
  - Headers (h1-h6 tags)
  - Links (all anchor tags)
  - Paragraphs (p tags)
  - Images (img tags with alt text and sources)
  - Audio Files (audio tags, source elements, and audio file links)
  - Tables (extracted as structured data)
  - All text content (complete page text)
- **💾 Export Options**: Download results as CSV, TXT, or JSON
- **⚙️ Configurable Settings**: Adjustable wait time for JavaScript rendering
- **🎨 Modern UI**: Clean, intuitive interface built with Streamlit
- **🔧 Automatic Driver Management**: Uses webdriver-manager for hassle-free ChromeDriver setup
- **🛡️ Error Handling**: Robust error handling for timeouts and WebDriver issues

## 📋 Prerequisites

- Python 3.7 or higher
- Google Chrome browser installed
- Internet connection

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Web_Scraper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Usage

1. **Start the Streamlit application**:
   ```bash
   streamlit run app.py
   ```

2. **The application will open in your default browser** (usually at `http://localhost:8501`)

3. **Use the application**:
   - Enter the URL you want to scrape in the input field
   - Select the scraping options from the sidebar (headers, links, paragraphs, images, audio files, tables, or all text)
   - Adjust the wait time slider if needed (default: 5 seconds)
   - Click the "🚀 Scrape Website" button
   - View the results in expandable sections
   - For audio files, you can preview them directly in the app using the built-in audio players
   - Download the data in your preferred format (CSV, TXT, or JSON)

## 📁 Project Structure

```
Web_Scraper/
│
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── import requests.py              # Example: Static website scraping with requests
└── import requests  dynamic websites.py  # Example: Dynamic website scraping with Selenium
```

## 🔧 Configuration

### Wait Time
Adjust the wait time slider in the sidebar to control how long the browser waits for JavaScript to render. This is especially useful for slow-loading websites or pages with heavy JavaScript content.

### Scraping Options
Select one or more options from the sidebar:
- **Headers**: Extracts all heading tags (h1 through h6)
- **Links**: Extracts all anchor tags with their href attributes
- **Paragraphs**: Extracts all paragraph text
- **Images**: Extracts image sources and alt text
- **Audio Files**: Extracts audio files from:
  - `<audio>` tags with `src` attributes
  - `<source>` elements within `<audio>` tags
  - Links pointing to audio file formats (.mp3, .wav, .ogg, .m4a, .flac, .aac, .wma, .opus, .webm)
  - Any element with `src` attribute pointing to audio files
  - Audio files are displayed with embedded players for direct playback
- **Tables**: Extracts table data as structured DataFrames
- **All Text**: Extracts all text content from the page

## 📦 Dependencies

- **streamlit**: Web application framework
- **selenium**: Web browser automation
- **beautifulsoup4**: HTML parsing
- **pandas**: Data manipulation and export
- **webdriver-manager**: Automatic ChromeDriver management
- **requests**: HTTP library (for example scripts)

## 🎨 Example Usage

### Basic Scraping
1. Enter URL: `https://example.com`
2. Select "Headers" and "Links"
3. Click "Scrape Website"
4. View and download results

### Advanced Scraping
1. Enter URL: `https://dynamic-website.com`
2. Select all scraping options
3. Increase wait time to 8 seconds for slow-loading content
4. Click "Scrape Website"
5. Preview audio files directly in the app
6. Export all data as JSON

### Audio File Extraction
1. Enter URL: `https://website-with-audio.com`
2. Select "Audio Files" option
3. Click "Scrape Website"
4. View audio files in a table with metadata
5. Use the embedded audio players to preview files directly
6. Download the audio file list as CSV

## 🐛 Troubleshooting

### ChromeDriver Issues
The application uses `webdriver-manager` to automatically download and manage ChromeDriver. If you encounter issues:
- Ensure Google Chrome is installed and up to date
- Check your internet connection (required for initial driver download)
- Try updating Chrome to the latest version

### Timeout Errors
If you get timeout errors:
- Increase the wait time in the sidebar
- Check if the website is accessible
- Verify the URL is correct

### Memory Issues
For very large websites:
- Select only the scraping options you need
- Consider scraping in smaller batches
- Close the browser between scraping sessions

## 📝 Notes

- The application runs in headless mode by default (no visible browser window)
- Some websites may have anti-scraping measures; use responsibly and respect robots.txt
- Always check the website's terms of service before scraping
- The scraper waits for JavaScript to render, making it suitable for Single Page Applications (SPAs)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

Created as part of the Web Scraper project.

## 🙏 Acknowledgments

- Streamlit for the amazing web app framework
- Selenium for web automation capabilities
- BeautifulSoup for HTML parsing
- webdriver-manager for simplified driver management

---

**Happy Scraping! 🚀**

