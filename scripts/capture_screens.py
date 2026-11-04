import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

os.makedirs("presentation/screenshots", exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

print("Launching Chrome WebDriver...")
driver = webdriver.Chrome(options=chrome_options)

views_to_capture = [
    ("", "01_landing_page.png", 5),
    ("?view=executive", "02_executive_overview.png", 4),
    ("?view=bola", "03_bola_findings.png", 4),
    ("?view=graph", "04_exposure_graph.png", 6),  # extra time for Plotly WebGL
    ("?view=semantic", "05_semantic_delta.png", 4),
    ("?view=isolation", "06_tenant_isolation_tifi.png", 4),
    ("?view=certificate", "07_forensic_certificate.png", 4),
    ("?view=reports", "08_ai_incident_report.png", 4),
    ("?view=benchmark", "09_research_benchmark.png", 4),
]

try:
    for query, filename, wait_sec in views_to_capture:
        url = f"http://127.0.0.1:8501/{query}"
        print(f"Loading {url} ...")
        driver.get(url)
        time.sleep(wait_sec)
        dest = os.path.join("presentation", "screenshots", filename)
        driver.save_screenshot(dest)
        size_kb = os.path.getsize(dest) / 1024
        print(f"  -> Saved {filename} ({size_kb:.1f} KB)")

    print("\n[SUCCESS] All 9 genuine application screenshots successfully captured!")

finally:
    driver.quit()
