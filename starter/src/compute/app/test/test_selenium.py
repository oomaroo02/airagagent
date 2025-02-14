# hello_world.py

import sys
from selenium import webdriver
from selenium import webdriver
import json
import os
import base64

def chrome_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument(f"--user-data-dir=/home/opc/chrome_profile")
    settings = {
        "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }
    prefs = {
        'printing.print_preview_sticky_settings.appState': json.dumps(settings),
        'savefile.default_directory': '/tmp/',
        'download.default_directory': '/tmp/',
        'plugins.plugins_disabled': "Chrome PDF Viewer",
        'plugins.always_open_pdf_externally': "true"
    }    
    options.add_experimental_option('prefs', prefs)
    options.add_argument('--kiosk-printing')  
    driver = webdriver.Chrome(options=options)
    return driver

if __name__ == '__main__':
    driver = chrome_webdriver()
    driver.get("https://google.com")
    driver.implicitly_wait(10)
    print(driver.title)
    driver.execute_script('window.print();')

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
    output_filename = "google.pdf"
    with open(output_filename, "wb") as f:
        f.write(bytes(base64.b64decode(pdf_data)))

    print(f"Webpage saved as {output_filename}")
        
    driver.quit()


