# apec_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def scrape_apec_jobs(keyword, pages=3):
    # Convert keyword to URL-safe string
    search_keyword = keyword.replace(" ", "%20")

    # Setup Chrome WebDriver
    chromedriver_path = "chromedriver.exe"
    options = Options()
    options.add_argument("--headless")  # ✅ Run without opening browser
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service,options=options)

    # Container for job data
    jobs = {
        "Title": [], "Company": [], "Description": [],
        "Salaire": [], "Type_Contrat": [], "Localisation": [], "Date_Publication": []
    }

    for page in range(pages):
        print(f"Scraping page {page}...")
        driver.get(f'https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles={search_keyword}&page={page}')
        time.sleep(2)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'card-offer__company'))
            )
        except:
            print("⚠️ Page took too long to load or no job cards found.")
            continue

        job_board = driver.find_elements(By.CLASS_NAME, 'card-offer__text')

        for offre in job_board:
            def safe_text(by, val):
                try:
                    return offre.find_element(by, val).text
                except:
                    return "N/A"

            jobs['Title'].append(safe_text(By.CLASS_NAME, 'card-title '))
            jobs['Company'].append(safe_text(By.CLASS_NAME, 'card-offer__company '))
            jobs['Description'].append(safe_text(By.CLASS_NAME, 'card-offer__description'))
            jobs['Salaire'].append(safe_text(By.TAG_NAME, 'li'))

            try:
                ul = offre.find_element(By.XPATH, './/ul[@class="details-offer important-list"]')
                li = ul.find_elements(By.TAG_NAME, "li")
                jobs['Type_Contrat'].append(li[0].text if len(li) > 0 else "N/A")
                jobs['Localisation'].append(li[1].text if len(li) > 1 else "N/A")
                jobs['Date_Publication'].append(li[2].text if len(li) > 2 else "N/A")
            except:
                jobs['Type_Contrat'].append("N/A")
                jobs['Localisation'].append("N/A")
                jobs['Date_Publication'].append("N/A")

        print(f"✅ Done page {page}")
        time.sleep(1)

    driver.quit()

    df = pd.DataFrame(jobs)
    return df  # You can later export if needed

#print(scrape_apec_jobs())
