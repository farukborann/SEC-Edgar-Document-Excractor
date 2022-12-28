from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

search_keyword = "DEF 14A"

ciks = ["0001390162",
        "0001399315",
        "0001401564",
        "0001404296",
        "0001404306",
        "0001406251",
        "0001407067",
        "3146",
        "3570",
        "4447",
        "10048",
        "10254",
        "29834",
        "33015"
        ]


def getUrl(cik: str):
    cik.lstrip(cik)
    return "https://www.sec.gov/edgar/browse/?CIK=" + cik + "&owner=exclude"

def getDocuments(html):
    table = BeautifulSoup(html, "html.parser")
    documents = table.find_all('tr', role='row')

    docs = []
    for document in documents:
        if(document.get('style') == "height: 0px;"):
            continue
        
        filing_date = document.find("td", class_="sorting_1").text
        href = document.find('a', class_='document-link').get('href')
        url = urljoin("https://www.sec.gov/", href)
        docs.append({"url": url, "filing_date": filing_date})

    return docs

def main():
    options = Options()
    # options.add_argument("disable-gpu")
    # options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    options.add_argument("window-size=1920,1080")

    cik_docs = []
    for cik in ciks:
        driver.get(getUrl(cik))
        #Wait untile site load
        try:
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "entityInformationHeader")))
            driver.execute_script("""document.querySelector('div[id="filings"]').classList.remove('hidden')""")
        except Exception:
            print("CIK => " + cik + " || Company Page doesnt include filings section or site cant loaded!!!")
            continue

        driver.find_element(By.ID, "filingDateFrom").clear()
        driver.find_element(By.ID, "filingDateTo").clear()
        driver.find_element(By.ID, "searchbox").send_keys(search_keyword)
        docs = getDocuments(driver.find_element(By.CLASS_NAME, "dataTables_scrollBody").get_attribute('outerHTML'))
        cik_docs.append({ "cik": cik, "docs": docs })
        print(cik + " => Done - Docs Count => " + str(len(docs)))

    driver.quit()

    file = open("results.json", "w", encoding="utf-8")
    json.dump(cik_docs, file, ensure_ascii=False, indent=2)
    file.close()


main()

# I coded a selenium bot that does the search you want and finds the documents and writes their urls and filing data to a json file