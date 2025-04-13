from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import pandas as pd
import random

def scrape_indeed_jobs(search_keyword="data+scientist", pages=3):
    # Setup Chrome WebDriver in headless mode
    chromedriver_path = "chromedriver.exe"
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=fr-FR")
    
    service = Service(chromedriver_path)
    driver = uc.Chrome(headless=False)  # set to True if needed
    #driver = webdriver.Chrome(service=service, options=options)
    time.sleep(random.uniform(2.5, 5.5))
    jobs = {
        "Title": [], "Company": [], "Location": [], "Date": [], "Summary": []
    }

    for page in range(0, pages * 10, 10):  # 10 results per page
        print(f"🔍 Scraping page {page // 10 + 1}...")

        url = f"https://fr.indeed.com/jobs?q={search_keyword}&l=Paris+(75)&radius=25&start={page}"
        driver.get(url)
        time.sleep(2)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon"))
            )
        except:
            print("⚠️ Page did not load properly.")
            continue

        job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")

        for card in job_cards:
            def safe(by, val):
                try:
                    return card.find_element(by, val).text
                except:
                    return "N/A"

            jobs['Title'].append(safe(By.CLASS_NAME, "jobTitle"))
            jobs['Company'].append(safe(By.CLASS_NAME, "companyName"))
            jobs['Location'].append(safe(By.CLASS_NAME, "companyLocation"))
            jobs['Date'].append(safe(By.CLASS_NAME, "date"))
            jobs['Summary'].append(safe(By.CLASS_NAME, "job-snippet"))
            # Random delay to mimic human behavior
        time.sleep(random.uniform(2.5, 5.5))
    driver.quit()
    df = pd.DataFrame(jobs)
    return df
print(scrape_indeed_jobs())