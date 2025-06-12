from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import re

# 일일 횟수 제한이 끝났을 때 변경해서 사용
SERVICE_KEY3 = "m8phIfnGb0sGF6Z2uz6bScSiENtALCEKYxPfz2Af9ZdfT0cVRAJRhRnFpH0uQkjLatM7OY7Js37PT8IM1cq8xQ=="

# 시도명 표준화 매핑
SIDO_NORMALIZE = {
    "서울": "서울특별시", "서울시": "서울특별시", "서울특별시": "서울특별시",
    "부산": "부산광역시", "부산시": "부산광역시", "부산광역시": "부산광역시",
    "대구": "대구광역시", "대구시": "대구광역시", "대구광역시": "대구광역시",
    "인천": "인천광역시", "인천시": "인천광역시", "인천광역시": "인천광역시",
    "광주": "광주광역시", "광주시": "광주광역시", "광주광역시": "광주광역시",
    "대전": "대전광역시", "대전시": "대전광역시", "대전광역시": "대전광역시",
    "울산": "울산광역시", "울산시": "울산광역시", "울산광역시": "울산광역시",
    "세종": "세종특별자치시", "세종시": "세종특별자치시", "세종특별자치시": "세종특별자치시",
    "경기": "경기도", "경기도": "경기도",
    "강원": "강원특별자치도", "강원도": "강원특별자치도", "강원특별자치도": "강원특별자치도",
    "충북": "충청북도", "충청북도": "충청북도",
    "충남": "충청남도", "충청남도": "충청남도",
    "전북": "전북특별자치도", "전라북도": "전북특별자치도", "전북특별자치도": "전북특별자치도",
    "전남": "전라남도", "전라남도": "전라남도",
    "경북": "경상북도", "경상북도": "경상북도",
    "경남": "경상남도", "경상남도": "경상남도",
    "제주": "제주특별자치도", "제주도": "제주특별자치도", "제주특별자치도": "제주특별자치도"
}

def normalize_sido(sido):
    for key, value in SIDO_NORMALIZE.items():
        if key in sido:
            return value
    return sido

def get_city_weather():
    url = "https://www.weather.go.kr/w/observation/land/city-obs.do"

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-blink-features=AutomationControlled')

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
        return []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    table = soup.find("table", class_="table-col")
    if table is None:
        print("테이블을 찾을 수 없습니다.")
        return []

    rows = table.find_all("tr")[1:]
    result = []

    for row in rows:
        city = row.find("th").text.strip()
        cols = row.find_all("td")
        if len(cols) < 11:
            continue

        try:
            hour = int(datetime.now().strftime('%H'))
            temp = float(cols[4].text.strip())
            sensible_temp = float(cols[6].text.strip())
            humidity = int(cols[8].text.strip())
            wind = float(cols[10].text.strip())
            weather = cols[0].text.strip()

            result.append({
                'city': city,
                'hour': hour,
                'temperature': temp,
                'sensible_temperature': sensible_temp,
                'humidity': humidity,
                'wind_speed': wind,
                'rain_type': weather
            })
        except:
            continue

    return result


def get_weather_by_city(target_city):
    # 전체 날씨 데이터를 위 함수를 통해 불러옴
    all_data = get_city_weather()
    matched_data = []

    for entry in all_data:
        city_name = entry.get("city")
        if city_name and target_city in city_name:
            matched_data.append(entry)

    return matched_data