from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import xml.etree.ElementTree as ET
from xml.dom import minidom
import csv

# ตั้งค่า browser
options = Options()
# options.add_argument("--headless")  # ปิด browser ขณะรันถ้าไม่ต้องการเห็น

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("กำลังเปิดเว็บไซต์...")
    driver.get("https://www.mytcas.com/")
    
    # รอให้หน้าเว็บโหลดเสร็จแบบเต็ม
    time.sleep(7)

    # รอจน search box โหลด
    search_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "search"))
    )

    keyword = "วิศวกรรมปัญญาประดิษฐ์"
    print(f"กำลังพิมพ์คำค้น: '{keyword}'")
    search_input.clear()
    search_input.send_keys(keyword)
    
    print("กำลังกด Enter...")
    search_input.send_keys(Keys.ENTER)

    # รอให้ URL เปลี่ยน และ AJAX โหลดเสร็จ
    time.sleep(5)  # รอ URL เปลี่ยน
    time.sleep(5)  # รอ AJAX โหลดเสร็จ

    # ตรวจสอบว่ามี div#results.t-result และ ul.t-programs
    result_container = driver.find_element(By.CSS_SELECTOR, "div#results.t-result")
    ul = result_container.find_element(By.CSS_SELECTOR, "ul.t-programs")
    li_elements = ul.find_elements(By.TAG_NAME, "li")
    print(f"พบ {len(li_elements)} รายการ")

    result = []
    skipped_items = []  # เก็บรายการที่ถูกข้าม
    
    # เปลี่ยน keyword ที่ใช้ตรวจสอบ
    prevent = 'ปัญญาประดิษฐ์'

    for index, li in enumerate(li_elements):
        try:
            a_tag = li.find_element(By.TAG_NAME, "a")
            href = a_tag.get_attribute("href")

            # ตรวจสอบว่ามี h3 หรือไม่ และมี keyword หรือไม่
            h3 = a_tag.find_element(By.TAG_NAME, "h3")
            
            # --- แสดงข้อมูลที่ถูกข้าม ---
            if prevent not in h3.text:
                skipped_info = {
                    "ลำดับ": index + 1,
                    "h3_text": h3.text.strip(),
                    "เหตุผล": f"ไม่มีคำว่า '{prevent}'"
                }
                skipped_items.append(skipped_info)
                print(f"❌ ข้ามรายการที่ {index + 1}: {h3.text.strip()}")
                continue  # ข้ามถ้าไม่มี keyword

            # --- ดึงชื่อหลักสูตร ---
            course_title = "ไม่พบชื่อหลักสูตร"
            try:
                # ลองหา <strong> ใน <h3> ก่อน
                course_title = h3.find_element(By.TAG_NAME, "strong").text.strip()
            except:
                # ถ้าไม่มี ให้ใช้ข้อความทั้งหมดใน h3
                course_title = h3.text.strip()
            
            # --- ดึงชื่อมหาวิทยาลัย ---
            university_name = "ไม่พบชื่อมหาวิทยาลัย"
            try:
                # หา span สุดท้ายใน a_tag
                spans = a_tag.find_elements(By.TAG_NAME, "span")
                if spans:
                    university_name = spans[-1].text.strip()
            except:
                pass

            item_data = {
                "มหาวิทยาลัย": university_name,
                "หลักสูตร": course_title,
                "ลิงก์": href
            }
            result.append(item_data)
            print(f"✅ บันทึกรายการที่ {index + 1}: {course_title}")

        except Exception as e:
            error_info = {
                "ลำดับ": index + 1,
                "เหตุผล": f"Error: {str(e)}"
            }
            skipped_items.append(error_info)
            print(f"⛔ ข้ามรายการที่ {index + 1} (error): {e}")
            continue

    # แสดงผลลัพธ์ทั้งหมด
    print("\n" + "="*50)
    print("✅ ผลลัพธ์ที่ผ่านการกรอง:")
    print("="*50)
    for i, item in enumerate(result, 1):
        print(f"{i}. {item['มหาวิทยาลัย']} - {item['หลักสูตร']}")

    # แสดงรายการที่ถูกข้าม
    print("\n" + "="*50)
    print("❌ รายการที่ถูกข้าม:")
    print("="*50)
    for item in skipped_items:
        print(f"ลำดับ {item['ลำดับ']}: {item.get('h3_text', 'N/A')} - {item['เหตุผล']}")

    # บันทึกเป็น XML
    print("\nกำลังบันทึกผลลัพธ์เป็นไฟล์ XML...")
    root = ET.Element("ผลลัพธ์การค้นหา")
    root.set("คำค้น", keyword)
    root.set("จำนวน", str(len(result)))

    for item in result:
        program = ET.SubElement(root, "หลักสูตร")
        ET.SubElement(program, "มหาวิทยาลัย").text = item["มหาวิทยาลัย"]
        ET.SubElement(program, "ชื่อหลักสูตร").text = item["หลักสูตร"]
        ET.SubElement(program, "ลิงก์").text = item["ลิงก์"]

    # จัดรูปแบบ XML ให้อ่านง่าย
    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")

    # บันทึกไฟล์
    with open("data/raw_aie.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        
        # เขียนหัวตาราง
        writer.writerow(["ลำดับ", "มหาวิทยาลัย", "หลักสูตร", "ลิงก์"])
        
        # เขียนข้อมูลแต่ละแถว
        for i, item in enumerate(result, 1):
            writer.writerow([
                i,
                item["มหาวิทยาลัย"],
                item["หลักสูตร"],
                item["ลิงก์"]
            ])
    
    print("✅ บันทึกไฟล์ 'raw_aie.csv' เสร็จสิ้น")

except Exception as e:
    print("เกิดข้อผิดพลาดหลัก:", str(e))

finally:
    driver.quit()
    print("จบการทำงาน")