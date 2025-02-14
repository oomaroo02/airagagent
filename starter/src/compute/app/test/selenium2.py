from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import shutil  # For removing the temporary directory
import time
import os

def download_webpage_as_pdf(url, output_filename="downloaded_page.pdf"):
    """
    Downloads a webpage as a PDF using Selenium and Chrome.

    Args:
        url: The URL of the webpage to download.
        output_filename: The name of the PDF file to save (default: "downloaded_page.pdf").
    """

    try:

        # 1. Set up Chrome options (headless for background execution - optional)
        chrome_options = Options()
        #chrome_options.add_argument("--headless=new")  # Run Chrome in headless mode (no visible window) - optional
        chrome_options.add_argument("--disable-gpu") # recommended for headless mode
        chrome_options.add_argument("--no-sandbox") # recommended for headless mode
        chrome_options.add_argument("--disable-dev-shm-usage") # recommended for headless mode
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--kiosk-printing')          
        temp_dir = tempfile.mkdtemp()
        print( "TEMP_DIR:" + temp_dir )
        chrome_options.add_argument(f"--user-data-dir={temp_dir}") # Use temporary directory

        # 2. Initialize ChromeDriver (replace with your ChromeDriver path if needed)
        #  It is best practice to use a webdriver manager like webdriver_manager to avoid hardcoding paths.
        driver = webdriver.Chrome(options=chrome_options)

        # 3. Navigate to the URL
        driver.get(url)

        # 4. Wait for the page to load (important! Adjust timeout as needed)
        # You might need to adjust the waiting strategy based on the website.
        # Here are a few options:

        # Option 1: Implicit wait (waits for elements to be available)
        driver.implicitly_wait(10)  # Wait up to 10 seconds

        # Option 2: Explicit wait (waits for a specific condition) - More robust
        # Example: wait for a specific element to be present
        # try:
        #     element_present = EC.presence_of_element_located((By.TAG_NAME, 'body')) # Example: wait for the <body> tag
        #     WebDriverWait(driver, 20).until(element_present) # Wait up to 20 seconds
        # except Exception as e:
        #     print(f"Error waiting for element: {e}")

        # Option 3: Simple sleep (less recommended, but sometimes necessary)
        # time.sleep(5)  # Wait for 5 seconds

        # 5. Generate PDF
        print_options = {
            "pageRanges": "1-1",  # Print all pages (you can customize this)
            "marginsType": 1,      # Set margins (0 = default, 1 = no margins, 2 = minimal margins)
            "printBackground": True, # Print background graphics
        }
        params = {'behavior': 'default', 'downloadPath': os.getcwd()} # Set the download directory to current working directory
        driver.execute_cdp_cmd('Page.setDownloadBehavior', params) # Set the download path for the PDF
        result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
        pdf_data = result['data']

        # 6. Save PDF to file
        with open(output_filename, "wb") as f:
            f.write(bytes(pdf_data, 'base64'))

        print(f"Webpage saved as {output_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if 'driver' in locals():
            driver.quit()
        # 2. Remove the temporary directory (important!)
        try:
            # shutil.rmtree(temp_dir) # Clean up after yourself
            print("Removed temporary user data directory.")
        except Exception as e:
            print(f"Error removing temporary directory: {e}")


# Example usage:
url_to_download = "https://www.example.com"  # Replace with the URL you want to download
output_pdf_file = "example_page.pdf"
download_webpage_as_pdf(url_to_download, output_pdf_file)

url_to_download = "https://www.google.com"  # Replace with the URL you want to download
output_pdf_file = "google_page.pdf"
download_webpage_as_pdf(url_to_download, output_pdf_file)