import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import re
import os
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from webdriver_manager.chrome import ChromeDriverManager

# Page configuration
st.set_page_config(
    page_title="Web Scraper with Selenium",
    page_icon="🌐",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = None
if 'driver' not in st.session_state:
    st.session_state.driver = None

def setup_driver(headless=False):
    """Setup Chrome WebDriver with options"""
    try:
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Use webdriver_manager to automatically handle ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"Error setting up WebDriver: {str(e)}")
        return None

def extract_audio_files(soup, base_url, driver=None):
    """Extract audio files from the page using both BeautifulSoup and Selenium"""
    audio_files = []
    audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.opus', '.webm']
    seen_urls = set()  # Track URLs to avoid duplicates
    
    def add_audio_file(audio_info):
        """Helper function to add audio file if not duplicate"""
        source_url = audio_info.get('source', '')
        if source_url and source_url not in seen_urls:
            seen_urls.add(source_url)
            audio_files.append(audio_info)
    
    # Method 1: Extract from <audio> tags using BeautifulSoup
    audio_tags = soup.find_all('audio')
    for audio in audio_tags:
        # Check src attribute
        if audio.get('src'):
            src = audio.get('src')
            absolute_url = urljoin(base_url, src)
            add_audio_file({
                'type': 'audio_tag',
                'source': absolute_url,
                'controls': audio.get('controls') is not None,
                'autoplay': audio.get('autoplay') is not None,
                'loop': audio.get('loop') is not None
            })
        
        # Check <source> tags within <audio>
        sources = audio.find_all('source', src=True)
        for source in sources:
            src = source.get('src')
            if src:
                absolute_url = urljoin(base_url, src)
                add_audio_file({
                    'type': 'audio_source',
                    'source': absolute_url,
                    'type_attr': source.get('type', 'Unknown'),
                    'controls': audio.get('controls') is not None
                })
    
    # Method 2: Use Selenium to find audio elements directly (handles dynamic content)
    if driver:
        try:
            # Find all audio elements using Selenium
            selenium_audio_elements = driver.find_elements(By.TAG_NAME, 'audio')
            for audio_elem in selenium_audio_elements:
                try:
                    # Get src attribute
                    src = audio_elem.get_attribute('src')
                    if src:
                        absolute_url = urljoin(base_url, src)
                        add_audio_file({
                            'type': 'audio_tag_selenium',
                            'source': absolute_url,
                            'controls': audio_elem.get_attribute('controls') is not None,
                            'autoplay': audio_elem.get_attribute('autoplay') is not None,
                            'loop': audio_elem.get_attribute('loop') is not None
                        })
                    
                    # Get source elements within audio
                    source_elements = audio_elem.find_elements(By.TAG_NAME, 'source')
                    for source_elem in source_elements:
                        src = source_elem.get_attribute('src')
                        if src:
                            absolute_url = urljoin(base_url, src)
                            add_audio_file({
                                'type': 'audio_source_selenium',
                                'source': absolute_url,
                                'type_attr': source_elem.get_attribute('type') or 'Unknown'
                            })
                except Exception as e:
                    continue
            
            # Find audio URLs in JavaScript variables and data attributes
            try:
                # Execute JavaScript to find audio URLs in various places
                js_code = r"""
                var audioUrls = [];
                // Find all audio elements
                document.querySelectorAll('audio').forEach(function(audio) {
                    if (audio.src) audioUrls.push(audio.src);
                    audio.querySelectorAll('source').forEach(function(source) {
                        if (source.src) audioUrls.push(source.src);
                    });
                });
                // Find audio in data attributes
                document.querySelectorAll('[data-audio], [data-src], [data-url]').forEach(function(el) {
                    var url = el.getAttribute('data-audio') || el.getAttribute('data-src') || el.getAttribute('data-url');
                    if (url && /\.(mp3|wav|ogg|m4a|flac|aac|wma|opus|webm)/i.test(url)) {
                        audioUrls.push(url);
                    }
                });
                // Find audio URLs in style backgrounds
                var allElements = document.querySelectorAll('*');
                allElements.forEach(function(el) {
                    var style = window.getComputedStyle(el);
                    var bg = style.backgroundImage || style.background;
                    if (bg && /\.(mp3|wav|ogg|m4a|flac|aac|wma|opus|webm)/i.test(bg)) {
                        var match = bg.match(/url\(['"]?([^'"]+)['"]?\)/);
                        if (match && match[1]) audioUrls.push(match[1]);
                    }
                });
                return audioUrls;
                """
                js_audio_urls = driver.execute_script(js_code)
                if js_audio_urls:
                    for url in js_audio_urls:
                        if url:
                            absolute_url = urljoin(base_url, url)
                            add_audio_file({
                                'type': 'audio_javascript',
                                'source': absolute_url
                            })
            except Exception as e:
                pass
        except Exception as e:
            pass
    
    # Method 3: Extract from links pointing to audio files
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href')
        if href:
            # Check if link points to an audio file
            parsed_url = urlparse(href)
            path_lower = parsed_url.path.lower()
            if any(path_lower.endswith(ext) for ext in audio_extensions):
                absolute_url = urljoin(base_url, href)
                add_audio_file({
                    'type': 'audio_link',
                    'source': absolute_url,
                    'link_text': link.get_text(strip=True) or 'No text'
                })
    
    # Method 4: Extract from any element with src pointing to audio files
    all_elements = soup.find_all(src=True)
    for element in all_elements:
        src = element.get('src')
        if src:
            parsed_url = urlparse(src)
            path_lower = parsed_url.path.lower()
            if any(path_lower.endswith(ext) for ext in audio_extensions):
                absolute_url = urljoin(base_url, src)
                add_audio_file({
                    'type': 'audio_src',
                    'source': absolute_url,
                    'tag': element.name
                })
    
    # Method 5: Search page source for audio URLs (regex pattern matching)
    if driver:
        try:
            page_source = driver.page_source
            # Pattern to find audio URLs in the page source
            audio_pattern = r'["\']([^"\']*\.(?:mp3|wav|ogg|m4a|flac|aac|wma|opus|webm)(?:\?[^"\']*)?)["\']'
            matches = re.findall(audio_pattern, page_source, re.IGNORECASE)
            for match in matches:
                if match:
                    absolute_url = urljoin(base_url, match)
                    add_audio_file({
                        'type': 'audio_regex',
                        'source': absolute_url
                    })
        except Exception as e:
            pass
    
    return audio_files

def download_audio_file(url, download_dir="downloads/audio"):
    """
    Download an audio file from a URL to the local system.
    
    Args:
        url: URL of the audio file to download
        download_dir: Directory to save the downloaded file (default: downloads/audio)
    
    Returns:
        tuple: (success: bool, file_path: str, error_message: str)
    """
    try:
        # Create download directory if it doesn't exist
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        
        # Get filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # If no filename in URL, generate one
        if not filename or '.' not in filename:
            # Try to get extension from content type or use .mp3 as default
            filename = f"audio_{int(time.time())}.mp3"
        else:
            # Sanitize filename
            filename = "".join(c for c in filename if c.isalnum() or c in ".-_")
        
        file_path = os.path.join(download_dir, filename)
        
        # Check if file already exists, add number suffix if needed
        counter = 1
        original_path = file_path
        while os.path.exists(file_path):
            name, ext = os.path.splitext(original_path)
            file_path = f"{name}_{counter}{ext}"
            counter += 1
        
        # Download the file
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # Save the file
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return True, file_path, None
        
    except requests.exceptions.RequestException as e:
        return False, None, f"Network error: {str(e)}"
    except Exception as e:
        return False, None, f"Error downloading file: {str(e)}"

def download_all_audio_files(audio_files, download_dir="downloads/audio"):
    """
    Download all audio files from a list of audio file dictionaries.
    
    Args:
        audio_files: List of dictionaries containing audio file information
        download_dir: Directory to save the downloaded files
    
    Returns:
        dict: Results with success count, failed count, and details
    """
    results = {
        'success': 0,
        'failed': 0,
        'downloaded_files': [],
        'failed_files': []
    }
    
    if not audio_files:
        return results
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_files = len(audio_files)
    
    for idx, audio_file in enumerate(audio_files):
        source_url = audio_file.get('source', '')
        if not source_url:
            results['failed'] += 1
            results['failed_files'].append({
                'url': 'No URL',
                'error': 'No source URL found'
            })
            continue
        
        status_text.text(f"Downloading {idx + 1}/{total_files}: {os.path.basename(urlparse(source_url).path)}")
        progress_bar.progress((idx + 1) / total_files)
        
        success, file_path, error = download_audio_file(source_url, download_dir)
        
        if success:
            results['success'] += 1
            results['downloaded_files'].append({
                'url': source_url,
                'file_path': file_path,
                'type': audio_file.get('type', 'Unknown')
            })
        else:
            results['failed'] += 1
            results['failed_files'].append({
                'url': source_url,
                'error': error
            })
    
    progress_bar.empty()
    status_text.empty()
    
    return results

def scrape_website(url, wait_time=5, scrape_options=None):
    """Scrape website using Selenium"""
    driver = None
    try:
        # Setup driver
        with st.spinner("Setting up browser..."):
            driver = setup_driver(headless=True)
            if not driver:
                return None
        
        # Navigate to URL
        with st.spinner(f"Loading {url}..."):
            driver.get(url)
            time.sleep(wait_time)  # Wait for JavaScript to render
        
        # Get page source after JavaScript execution
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        results = {}
        
        # Scrape based on selected options
        if scrape_options:
            if 'headers' in scrape_options:
                headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                results['headers'] = [{'tag': h.name, 'text': h.get_text(strip=True)} for h in headers]
            
            if 'links' in scrape_options:
                links = soup.find_all('a', href=True)
                results['links'] = [{'text': link.get_text(strip=True), 'url': link.get('href')} for link in links]
            
            if 'paragraphs' in scrape_options:
                paragraphs = soup.find_all('p')
                results['paragraphs'] = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
            
            if 'images' in scrape_options:
                images = soup.find_all('img', src=True)
                results['images'] = [{'alt': img.get('alt', 'No alt text'), 'src': img.get('src')} for img in images]
            
            if 'tables' in scrape_options:
                tables = soup.find_all('table')
                results['tables'] = []
                for table in tables:
                    try:
                        df = pd.read_html(str(table))[0]
                        results['tables'].append(df.to_dict('records'))
                    except:
                        pass
            
            if 'all_text' in scrape_options:
                results['all_text'] = soup.get_text(separator='\n', strip=True)
            
            if 'audio' in scrape_options:
                audio_files = extract_audio_files(soup, url, driver)
                results['audio'] = audio_files
        
        return results
    
    except TimeoutException:
        st.error("Timeout: The page took too long to load.")
        return None
    except WebDriverException as e:
        st.error(f"WebDriver error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None
    finally:
        if driver:
            driver.quit()

def main():
    # Header
    st.markdown('<h1 class="main-header">🌐 Web Scraper with Selenium</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        wait_time = st.slider("Wait Time (seconds)", min_value=1, max_value=10, value=5, 
                             help="Time to wait for JavaScript to render")
        st.markdown("---")
        st.markdown("### 📋 Scraping Options")
        scrape_headers = st.checkbox("Headers (h1-h6)", value=True)
        scrape_links = st.checkbox("Links (a tags)", value=True)
        scrape_paragraphs = st.checkbox("Paragraphs (p tags)", value=False)
        scrape_images = st.checkbox("Images (img tags)", value=False)
        scrape_audio = st.checkbox("Audio Files", value=False)
        scrape_tables = st.checkbox("Tables", value=False)
        scrape_all_text = st.checkbox("All Text Content", value=False)
        
        st.markdown("---")
        st.markdown("### 💾 Downloads")
        st.info("📁 Audio files are saved to: `downloads/audio/` folder")
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input("Enter URL to scrape:", placeholder="https://example.com")
    
    with col2:
        st.write("")  # Spacing
        scrape_button = st.button("🚀 Scrape Website", type="primary")
    
    # Prepare scrape options
    scrape_options = []
    if scrape_headers:
        scrape_options.append('headers')
    if scrape_links:
        scrape_options.append('links')
    if scrape_paragraphs:
        scrape_options.append('paragraphs')
    if scrape_images:
        scrape_options.append('images')
    if scrape_audio:
        scrape_options.append('audio')
    if scrape_tables:
        scrape_options.append('tables')
    if scrape_all_text:
        scrape_options.append('all_text')
    
    # Scrape button action
    if scrape_button:
        if not url:
            st.warning("⚠️ Please enter a URL")
        elif not url.startswith(('http://', 'https://')):
            st.warning("⚠️ Please enter a valid URL starting with http:// or https://")
        elif not scrape_options:
            st.warning("⚠️ Please select at least one scraping option")
        else:
            results = scrape_website(url, wait_time, scrape_options)
            st.session_state.scraped_data = results
    
    # Display results
    if st.session_state.scraped_data:
        st.markdown("---")
        st.header("📊 Scraping Results")
        
        results = st.session_state.scraped_data
        
        # Display headers
        if 'headers' in results and results['headers']:
            with st.expander(f"📝 Headers ({len(results['headers'])} found)", expanded=True):
                headers_df = pd.DataFrame(results['headers'])
                st.dataframe(headers_df, use_container_width=True)
                
                # Download button
                csv = headers_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Headers as CSV",
                    data=csv,
                    file_name="headers.csv",
                    mime="text/csv"
                )
        
        # Display links
        if 'links' in results and results['links']:
            with st.expander(f"🔗 Links ({len(results['links'])} found)", expanded=True):
                links_df = pd.DataFrame(results['links'])
                st.dataframe(links_df, use_container_width=True)
                
                # Download button
                csv = links_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Links as CSV",
                    data=csv,
                    file_name="links.csv",
                    mime="text/csv"
                )
        
        # Display paragraphs
        if 'paragraphs' in results and results['paragraphs']:
            with st.expander(f"📄 Paragraphs ({len(results['paragraphs'])} found)"):
                for i, para in enumerate(results['paragraphs'], 1):
                    st.write(f"**Paragraph {i}:**")
                    st.write(para)
                    st.write("---")
        
        # Display images
        if 'images' in results and results['images']:
            with st.expander(f"🖼️ Images ({len(results['images'])} found)"):
                images_df = pd.DataFrame(results['images'])
                st.dataframe(images_df, use_container_width=True)
                
                # Download button
                csv = images_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Images as CSV",
                    data=csv,
                    file_name="images.csv",
                    mime="text/csv"
                )
        
        # Display audio files
        if 'audio' in results and results['audio']:
            with st.expander(f"🎵 Audio Files ({len(results['audio'])} found)", expanded=True):
                audio_df = pd.DataFrame(results['audio'])
                st.dataframe(audio_df, use_container_width=True)
                
                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    csv = audio_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Audio List as CSV",
                        data=csv,
                        file_name="audio_files.csv",
                        mime="text/csv"
                    )
                with col2:
                    if st.button("💾 Download All Audio Files", type="primary"):
                        download_results = download_all_audio_files(results['audio'])
                        if download_results['success'] > 0:
                            st.success(f"✅ Successfully downloaded {download_results['success']} file(s) to 'downloads/audio' folder!")
                            if download_results['downloaded_files']:
                                with st.expander("📁 Downloaded Files", expanded=False):
                                    for file_info in download_results['downloaded_files']:
                                        st.write(f"✅ {os.path.basename(file_info['file_path'])}")
                                        st.caption(f"Source: {file_info['url']}")
                        if download_results['failed'] > 0:
                            st.warning(f"⚠️ Failed to download {download_results['failed']} file(s)")
                            if download_results['failed_files']:
                                with st.expander("❌ Failed Downloads", expanded=False):
                                    for file_info in download_results['failed_files']:
                                        st.write(f"❌ {file_info.get('url', 'Unknown')}")
                                        st.caption(f"Error: {file_info.get('error', 'Unknown error')}")
                
                # Display audio players for direct audio sources
                st.markdown("### 🎧 Audio Players")
                for i, audio_file in enumerate(results['audio'], 1):
                    source_url = audio_file.get('source', '')
                    if source_url:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**Audio {i}:**")
                            st.audio(source_url)
                            st.markdown(f"Source: [{source_url}]({source_url})")
                        with col2:
                            # Individual download button
                            if st.button(f"💾 Download", key=f"download_audio_{i}"):
                                with st.spinner(f"Downloading audio {i}..."):
                                    success, file_path, error = download_audio_file(source_url)
                                    if success:
                                        st.success(f"✅ Downloaded to: {file_path}")
                                    else:
                                        st.error(f"❌ Download failed: {error}")
                        st.markdown("---")
        
        # Display tables
        if 'tables' in results and results['tables']:
            with st.expander(f"📊 Tables ({len(results['tables'])} found)"):
                for i, table_data in enumerate(results['tables'], 1):
                    st.write(f"**Table {i}:**")
                    if table_data:
                        df = pd.DataFrame(table_data)
                        st.dataframe(df, use_container_width=True)
                    st.write("---")
        
        # Display all text
        if 'all_text' in results and results['all_text']:
            with st.expander("📝 All Text Content"):
                st.text_area("Full Text:", results['all_text'], height=400)
                
                # Download button
                st.download_button(
                    label="📥 Download All Text as TXT",
                    data=results['all_text'],
                    file_name="all_text.txt",
                    mime="text/plain"
                )
        
        # Download all data as JSON
        st.markdown("---")
        json_data = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="📥 Download All Data as JSON",
            data=json_data,
            file_name="scraped_data.json",
            mime="application/json"
        )
        
        # Clear button
        if st.button("🗑️ Clear Results"):
            st.session_state.scraped_data = None
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Built with ❤️ using Streamlit and Selenium</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

