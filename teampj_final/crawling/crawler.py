import time
import random
import json
import sys
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import chromedriver_autoinstaller

# 검색어를 인자로 받음
if len(sys.argv) < 2:
    print("검색어가 없습니다.")
    sys.exit(1)

search_place = sys.argv[1]

# 크롬드라이버 설치
chromedriver_autoinstaller.install()

# 크롬 옵션 설정
options = Options()
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)
options.add_argument("--headless")  # 필요 시 백그라운드 실행

# 브라우저 실행
driver = webdriver.Chrome(options=options)
driver.get("https://map.naver.com/v5")
time.sleep(random.uniform(2, 4))

# 검색 입력
try:
    search_input = driver.find_element(By.CLASS_NAME, "input_search")
    search_input.send_keys(search_place)
    search_input.send_keys(Keys.ENTER)
except:
    print("검색창 로딩 실패")
    driver.quit()
    sys.exit(1)

# 검색결과 프레임 전환
try:
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe"))
    )
except:
    print("searchIframe 이동 실패")
    driver.quit()
    sys.exit(1)

place_info = {}
index = 0

# 장소 리스트 수집
try:
    place_list = WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located(
        (By.XPATH, "//*[contains(@class, 'TYaxT') or contains(@class, 'YwYLL') or contains(@class, 'moQ_p') or contains(@class, 'CMy2_') or contains(@class, 'xBZDS')]")
    )
)
except:
    print("장소 목록 로딩 실패 — 검색어에 대한 결과 없음 또는 페이지 구조 변경됨")
    driver.quit()
    sys.exit(1)

end_index = min(index + 5, len(place_list))

for i in range(index, end_index):
    place_name = place_list[i].text.strip()
    if place_name in place_info:
        continue

    place_info[place_name] = {
        "review": [],
        "images": [],
        "location": "",
        "operate": "",
        "contact": "",
        "website": ""
    }

    time.sleep(1)
    
    # 장소 클릭
    try:
        click_target = place_list[i].find_element(
            By.XPATH, "./ancestor::a[contains(@class, 'place_bluelink')]"
        )
        click_target.click()
        time.sleep(2)
    except:
        print("장소 클릭 실패")
        continue

    try:
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "entryIframe"))
        )        
    except:
        print("entryIframe 이동 실패")
        continue

    # 상세정보 수집
    try:
        place_info[place_name]["location"] = (
            driver.find_element(By.CLASS_NAME, "LDgIH").text
        )
    except:
        place_info[place_name]["location"] = "--"

    try:
        place_info[place_name]["operate"] = (
            driver.find_element(By.CLASS_NAME, "A_cdD").text
        )
    except:
        place_info[place_name]["operate"] = "--"

    try:
        place_info[place_name]["contact"] = (
            driver.find_element(By.CLASS_NAME, "xlx7Q").text
        )
    except:
        place_info[place_name]["contact"] = "--"

    try:
        place_info[place_name]["website"] = (
            driver.find_element(By.CLASS_NAME, "CHmqa").text
        )
    except:
        place_info[place_name]["website"] = "--"

    # 리뷰 탭 클릭 및 수집
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='리뷰']"))
        ).click()
    except:
        print("리뷰 탭 클릭 실패")

    max_review = 80
    collected = 0
    scroll_count = 0
    max_scroll = 10

    while collected < max_review and scroll_count < max_scroll:
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        # time.sleep(1)
        review_list = driver.find_elements(By.XPATH, "//div[@class='pui__vn15t2']/a")

        for review in review_list:
            txt = review.text
            if txt and txt not in place_info[place_name]["review"] and txt != "더보기":
                place_info[place_name]["review"].append(txt)
                collected += 1
            if collected >= max_review:
                break

        scroll_count += 1
        try:
            driver.find_element(By.XPATH, "//a[@class='fvwqf']").click()
            time.sleep(1)
        except:
            continue

    try:
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)

        imgs = driver.find_elements(By.TAG_NAME, "img")
        print(f"[DEBUG] 총 img 태그 개수: {len(imgs)}")
        for idx, img in enumerate(imgs[:10]):
            print(f"[DEBUG] src#{idx}: {img.get_attribute('src')} | data-src#{idx}: {img.get_attribute('data-src')}")

        real_imgs = []
        for img in imgs:
            src = img.get_attribute('src') or img.get_attribute('data-src')
            if src and src.startswith("http"):
                real_imgs.append(src)
        place_info[place_name]["images"] = real_imgs[:5]
        print(f"[DEBUG] 저장된 이미지 URL: {place_info[place_name]['images']}")
    except Exception as e:
        print("이미지 수집 실패:", e)

    # 다시 searchIframe으로 복귀
    try:
        driver.switch_to.default_content()
        driver.switch_to.frame("searchIframe")
    except:
        print("searchIframe 복귀 실패")
        continue

# 이전 결과 삭제 후 저장
if os.path.exists("result.json"):
    os.remove("result.json")

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(place_info, f, ensure_ascii=False, indent=4)

print(f"[완료] '{search_place}' 검색 결과 저장됨.")

driver.quit()