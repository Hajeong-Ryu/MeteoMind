from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import requests
import urllib.parse
import time

def get_city_weather():
    url = "https://www.weather.go.kr/w/observation/land/city-obs.do"

    options = Options()
    options.add_argument('--headless')  # 창 안띄우고 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument("--remote-debugging-port=9222")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-col"))
        )
    except:
        print("시간 초과: 테이블을 찾지 못했습니다.")
        driver.quit()
        return None

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    table = soup.find("table", class_="table-col")
    if table is None:
        print("테이블을 찾을 수 없습니다. 다시 확인해 주세요")
        return

    rows = table.find_all("tr")[1:]  # 0번째는 header이므로 1번째부터 추출

    for row in rows:
        city = row.find("th").text.strip()  # 도시 이름
        cols = row.find_all("td")
        if len(cols) < 10:
            continue

        weather = cols[0].text.strip()  # 날씨
        temp = cols[4].text.strip()  # 기온
        sensible_temp = cols[6].text.strip()  # 체감온도
        humidity = cols[8].text.strip()  # 습도
        wind = cols[10].text.strip()  # 풍속

        print(f"도시 : {city}")
        print(f"기온: {temp}℃")
        print(f"체감온도: {sensible_temp}℃")
        print(f"습도: {humidity}%")
        print(f"날씨: {weather}")
        print(f"풍속: {wind}m/s")
        print()

# def check_risk(temp, humidity):


def get_pm(region, item_code):
    #item_code  
    #PM10 = 10007
    #PM2.5 = 10008  
    special_regions = {"서울", "인천", "대전", "세종", "부산", "광주", "대구", "울산", "제주"}
        
    # 1) Chrome 옵션 설정
    options = Options()
    # options.add_argument('--headless')    # 필요시 주석 해제
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # 2) 드라이버 실행
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 3) 페이지 접속 및 크기 설정
        driver.set_window_size(1920, 1080)
        driver.get(f"https://www.airkorea.or.kr/web/sidoQualityCompare?itemCode={item_code}&pMENU_NO=102")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "district"))
        )
        dropdown = Select(driver.find_element(By.ID, "district"))
        dropdown.select_by_visible_text(region)
        print("✅ 지역 선택 완료")

        search_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'검색')]"))
        )
        search_btn.click()
        print("✅ 검색 버튼 클릭 완료")
        
        # 4) sidoCharts2 내부의 context 버튼 클릭
        chart2_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sidoCharts2"))
        )
        
        context_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "highcharts-contextbutton"))
        )
        
        context_button = chart2_container.find_element(By.CLASS_NAME, "highcharts-contextbutton")
        ActionChains(driver).move_to_element(context_button).click().perform()
        print("✅ sidoCharts2 내부 버튼 클릭 성공")

        # 5) "View data table" (영/한) 클릭
        view_data = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//li[contains(@class,'highcharts-menu-item') and "
                "(contains(text(),'View data table') or contains(text(),'데이터 테이블 보기'))]"
            ))
        )
        view_data.click()
        print("✅ View data table 클릭 성공")

        # 6) charts2(#charts2) 내부 데이터 테이블이 뜰 때까지 대기 (driver 기준)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#charts2 .highcharts-data-table"))
        )
        print("✅ charts2 내부 테이블 로딩 완료")

        # 7) charts2 영역에서 테이블을 찾아 데이터 파싱
        charts2_div = driver.find_element(By.ID, "charts2")
        table = charts2_div.find_element(By.CLASS_NAME, "highcharts-data-table")
        rows = table.find_elements(By.TAG_NAME, "tr")

        # 8) 결과 출력
        pm_values = []
        print("\n📊 측정소별 PM 데이터:")
        for row in rows[1:]:  # 첫 행은 헤더
            try:
                station = row.find_element(By.TAG_NAME, "th").text
                value = row.find_elements(By.TAG_NAME, "td")[0].text
                print(f"{station} : {value}")
                try:
                    pm_values.append(float(value))
                except ValueError:
                    continue
            except Exception:
                continue
            
        if region in special_regions:
            if pm_values:
                avg_pm = round(sum(pm_values) / len(pm_values), 2)
                print(f"\n✅ {region} : {avg_pm}")
            else:
                print(f"\n❌ {region} 전체 측정소 PM 평균값을 계산할 수 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    finally:
        driver.quit()

get_pm("서울", 10007)   # 서울의 PM10 평균
get_pm("강원", 10008)   # 강원도의 각 측정소별 PM2.5