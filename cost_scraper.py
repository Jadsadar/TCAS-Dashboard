import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from webdriver_manager.chrome import ChromeDriverManager

def scrape_costs_from_dataframe(input_df):

    # ตั้งค่า ChromeDriver (headless ไม่เปิดหน้าต่าง)
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # คัดลอก DataFrame และเพิ่มคอลัมน์ใหม่สำหรับค่าใช้จ่าย
        df = input_df.copy()
        df["ค่าใช้จ่าย"] = ""

        # Loop ตามลิงก์ - ใช้ชื่อคอลัมน์ภาษาอังกฤษ
        for idx, row in df.iterrows():
            url = row["Link"]  # เปลี่ยนจาก "ลิงก์" เป็น "Link"
            try:
                driver.get(url)
                time.sleep(3)  # รอให้โหลด JavaScript
                
                soup = BeautifulSoup(driver.page_source, "html.parser")
                cost_dt = soup.find("dt", string="ค่าใช้จ่าย")
                if cost_dt:
                    cost_dd = cost_dt.find_next_sibling("dd")
                    if cost_dd:
                        df.at[idx, "ค่าใช้จ่าย"] = cost_dd.text.strip()
                    else:
                        df.at[idx, "ค่าใช้จ่าย"] = "ไม่พบ <dd>"
                else:
                    df.at[idx, "ค่าใช้จ่าย"] = "ไม่พบ <dt>ค่าใช้จ่าย</dt>"
            except Exception as e:
                df.at[idx, "ค่าใช้จ่าย"] = f"Error: {e}"
                
    finally:
        # ปิด browser
        driver.quit()
    
    return df

# Example usage:
if __name__ == "__main__":
    # You can test the function here if needed
    pass