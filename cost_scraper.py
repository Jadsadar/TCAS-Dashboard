import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from webdriver_manager.chrome import ChromeDriverManager

def scrape_costs_from_dataframe(input_df):
    """
    Scrapes cost, course name, and course type information from program detail pages.

    Args:
        input_df (pd.DataFrame): DataFrame containing program links in a 'Link' column.

    Returns:
        pd.DataFrame: Original DataFrame with added 'ค่าใช้จ่าย', 'Course Name', and 'Course Type' columns.
                      Note: 'Course Name' corresponds to 'ชื่อหลักสูตร',
                            'Course Type' corresponds to 'ประเภทหลักสูตร'.
    """
    # ตั้งค่า ChromeDriver (headless ไม่เปิดหน้าต่าง)
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox') # Added for stability
    options.add_argument('--disable-dev-shm-usage') # Added for stability
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # คัดลอก DataFrame และเพิ่มคอลัมน์ใหม่สำหรับข้อมูลที่ scrape
        df = input_df.copy()
        # Initialize columns with empty strings or a placeholder
        df["ค่าใช้จ่าย"] = ""
        df["Course Name"] = ""  # New column for ชื่อหลักสูตร (in Thai)
        df["Course Type"] = ""  # New column for ประเภทหลักสูตร

        # Loop ตามลิงก์ - ใช้ชื่อคอลัมน์ภาษาอังกฤษ
        for idx, row in df.iterrows():
            url = row["Link"]
            print(f"Scraping data for program {idx + 1}/{len(df)} from: {url}") # Optional: Progress indicator
            try:
                driver.get(url)
                # เพิ่ม wait time หรือใช้ WebDriverWait ถ้าจำเป็น
                time.sleep(3) # รอให้โหลด JavaScript

                soup = BeautifulSoup(driver.page_source, "html.parser")

                # --- Scrape ค่าใช้จ่าย ---
                cost_dt = soup.find("dt", string="ค่าใช้จ่าย")
                if cost_dt:
                    cost_dd = cost_dt.find_next_sibling("dd")
                    if cost_dd:
                        df.at[idx, "ค่าใช้จ่าย"] = cost_dd.text.strip()
                    else:
                        df.at[idx, "ค่าใช้จ่าย"] = "ไม่พบ <dd> สำหรับ ค่าใช้จ่าย"
                else:
                    df.at[idx, "ค่าใช้จ่าย"] = "ไม่พบ <dt>ค่าใช้จ่าย</dt>"

                # --- Scrape ชื่อหลักสูตร ---
                # ตามตัวอย่าง ใช้ <dt>ชื่อหลักสูตร</dt>
                name_dt = soup.find("dt", string="ชื่อหลักสูตร")
                if name_dt:
                    name_dd = name_dt.find_next_sibling("dd")
                    if name_dd:
                        df.at[idx, "Course Name"] = name_dd.text.strip()
                    else:
                        df.at[idx, "Course Name"] = "ไม่พบ <dd> สำหรับ ชื่อหลักสูตร"
                else:
                     # ถ้าไม่เจอ ลองหา <dt>ชื่อหลักสูตรภาษาอังกฤษ</dt> แทน?
                     # name_dt_alt = soup.find("dt", string="ชื่อหลักสูตรภาษาอังกฤษ")
                     # if name_dt_alt:
                     #     name_dd_alt = name_dt_alt.find_next_sibling("dd")
                     #     if name_dd_alt:
                     #         df.at[idx, "Course Name"] = name_dd_alt.text.strip() + " (English Name)"
                     #     else:
                     #         df.at[idx, "Course Name"] = "ไม่พบ <dd> สำหรับ ชื่อหลักสูตรภาษาอังกฤษ"
                     # else:
                     df.at[idx, "Course Name"] = "ไม่พบ <dt>ชื่อหลักสูตร</dt>"

                # --- Scrape ประเภทหลักสูตร ---
                type_dt = soup.find("dt", string="ประเภทหลักสูตร")
                if type_dt:
                    type_dd = type_dt.find_next_sibling("dd")
                    if type_dd:
                        df.at[idx, "Course Type"] = type_dd.text.strip()
                    else:
                        df.at[idx, "Course Type"] = "ไม่พบ <dd> สำหรับ ประเภทหลักสูตร"
                else:
                    df.at[idx, "Course Type"] = "ไม่พบ <dt>ประเภทหลักสูตร</dt>"

            except Exception as e:
                # หากเกิดข้อผิดพลาดกับ URL นี้ ให้บันทึกข้อความ error ไว้ในทุกคอลัมน์ที่ scrape
                error_msg = f"Error scraping page: {e}"
                df.at[idx, "ค่าใช้จ่าย"] = error_msg
                df.at[idx, "Course Name"] = error_msg
                df.at[idx, "Course Type"] = error_msg
                print(f"   Error for URL {url}: {e}") # Optional: Log the error

    finally:
        # ปิด browser
        driver.quit()
        print("WebDriver closed.") # Optional: Confirmation

    return df

# Example usage (if running this script directly):
# if __name__ == "__main__":
#     # Example DataFrame
#     # data = {'Link': ['https://www.mytcas.com/universities/1/programs/123', 'https://www.mytcas.com/universities/2/programs/456']}
#     # df_test = pd.DataFrame(data)
#     # df_result = scrape_costs_from_dataframe(df_test)
#     # print(df_result)
#     pass
