from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
import os

CHROME_DRIVER = "./chromedriver/"
CHROME_DRIVER_NAME = "chromedriver"

COMPANY_CODE_URL = "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201"

PATH = os.getcwd() + os.path.sep
DATA_PATH = PATH+"data"+os.path.sep

download_check = False

for filename in os.listdir(DATA_PATH):
    if 'data' in filename.split('/')[-1]:
        os.remove(DATA_PATH+filename)

options = ChromeOptions()
options.add_experimental_option("prefs", {
    "download.default_directory": DATA_PATH,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

print("Download COMPANY_CODE Info")

driver = webdriver.Chrome(service=Service(CHROME_DRIVER+CHROME_DRIVER_NAME), options=options)

driver.get(COMPANY_CODE_URL)
driver.implicitly_wait(10)

time.sleep(10)

driver.find_element(By.CLASS_NAME, "CI-MDI-UNIT-DOWNLOAD").click()
downloads = driver.find_element(By.CLASS_NAME, "filedown_wrap").find_elements(By.TAG_NAME, 'div')
for download in downloads:
    if download.get_attribute('data-type') == "csv":
        download.click()

while True:
    for filename in os.listdir(DATA_PATH):
        if 'data' in filename.split('/')[-1] and 'crdownload' not in filename.split('/')[-1]:
            download_check = True
            break
    if download_check is True:
        break

driver.quit()
