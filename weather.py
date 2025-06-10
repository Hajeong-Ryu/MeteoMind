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
    
    pm10_data = {}
    pm2_5_data = {}
    cities = []
    for row in rows:
        city = row.find("th").text.strip()  # 도시 이름
        cities.append(city)
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
        # print(f"PM10: {pm10} ㎍/m³")
        # print(f"PM2.5: {pm2_5} ㎍/m³")
        print()
        
        # print(cities)

# def check_risk(temp, humidity):

def get_city_pm(city):
    url = "https://www.weather.go.kr/w/index.do"
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    driver.get(url)

    pm10 = None
    pm25 = None

    try:
        # 지도 확대
        for _ in range(2):
            try:
                zoom_in = driver.find_element(By.CLASS_NAME, 'ol-zoom-in')
                zoom_in.click()
                time.sleep(0.5)
            except:
                print("지도 확대 버튼을 찾을 수 없습니다.")
                break
        
        # 도시명으로 마커 div 찾기
        target = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, f'//div[contains(@class,"sfc-main")]//span[@class="hid" and text()="{city}"]/parent::div')
            )
        )
        
        # 클릭
        driver.execute_script("arguments[0].click();", target)
        
        # 정보 갱신 대기
        def info_updated(driver):
            try:
                air_ul = driver.find_element(By.CSS_SELECTOR, 'div.aws-data-head > p')
                return city in air_ul.text
            except:
                return False

        WebDriverWait(driver, 10).until(info_updated)

        air_ul = driver.find_element(By.CSS_SELECTOR, 'ul.wrap-2.air-wrap.no-underline')
        li_list = air_ul.find_elements(By.TAG_NAME, 'li')

        for li in li_list:
            label = li.find_element(By.CSS_SELECTOR, 'span.lbl').text
            value = li.find_element(By.CSS_SELECTOR, 'span.air-lvv').text
            if '초미세먼지' in label:
                pm25 = value
            elif '미세먼지' in label and '초미세먼지' not in label:
                pm10 = value

        return {
            "pm10": pm10,
            "pm25": pm25
        }
        
    except Exception as e:
        print(f"{city} 마커 또는 대기질 정보를 찾을 수 없습니다: {e}")
        return {"pm10": pm10, "pm25": pm25}
    finally:
        driver.quit()
        