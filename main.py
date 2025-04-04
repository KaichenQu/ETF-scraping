import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def scrape_holdings(etf_code: str):
    url = f"https://www.etf.com/{etf_code}"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    time.sleep(6)

    try:
        holdings_btn = wait.until(EC.presence_of_element_located((By.ID, "fp-menu-holdings")))
        driver.execute_script("""
            const evt = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            arguments[0].dispatchEvent(evt);
        """, holdings_btn)
        time.sleep(2)
    except Exception:
        driver.quit()
        return []

    try:
        view_all_text_div = wait.until(EC.presence_of_element_located((By.XPATH, "//div[text()='VIEW ALL']")))
        view_all_button = view_all_text_div.find_element(
            By.XPATH,
            "./ancestor::div[contains(@class, 'cursor-pointer')]"
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", view_all_button)
        time.sleep(0.5)
        view_all_button.click()
    except Exception as e:
        print(f"[{etf_code}] Could not click VIEW ALL: {e}")
        driver.quit()
        return []

    results = []
    try:
        holdings = driver.find_elements(By.XPATH, "//div[contains(@class, 'w-full') and contains(@class, 'h-16')]")
        print(f"\nHoldings for {etf_code}:\n")
        for h in holdings:
            divs = h.find_elements(By.XPATH, ".//div")
            if len(divs) == 2:
                name = divs[0].text.strip()
                percent = divs[1].text.strip()
                results.append((name, percent))
                print(f"{name}: {percent}")
    except Exception as e:
        print(f"[{etf_code}] Failed to extract holdings: {e}")

    driver.quit()
    return results


if __name__ == '__main__':
    etfs = ["QQQ", "QLD", "TQQQ"]

    for etf in etfs:
        holdings = scrape_holdings(etf)

        # Optional: save each ETF's holdings to a CSV file
        if holdings:
            with open(f"{etf}_holdings.csv", mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Company", "Percentage"])
                writer.writerows(holdings)
            print(f"Saved {etf}_holdings.csv")
