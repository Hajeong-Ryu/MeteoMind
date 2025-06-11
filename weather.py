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
import pandas as pd
import re
import urllib.parse
import time

SERVICE_KEY = "KH5Jlc6te5pGBhMfqRKnpxz6EO/5mwdKBNo+rEpnBvbb+bh/dHQklTCzNKLWfdvq25SI93ImU7QbHg8GA4Jv6Q=="
SERVICE_KEY2 = 'ODyQFTdVk9FRQzWddNBQa/3GaxSl6mr+3xef7rM5v5IzNXxB1eVBDTql2a+ONM9krccUP0RBIyX+XLITm9jKGQ=='

def get_city_names():
    url = "https://www.weather.go.kr/w/observation/land/city-obs.do"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", class_="table-col")
    tbody = table.find("tbody")
    rows = tbody.find_all("tr")
    cities = [row.find("th").text.strip() for row in rows]
    return cities

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
    "강원": "강원특별자치도", "강원도": "강원특별자치도", "강원특별자치도": "강원특별자치도", "(산지)강원특별자치도": "강원특별자치도",
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
    return sido  # 매칭 안되면 원본 반환

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

        # pm_data = get_city_pm(city)
        # pm10 = pm_data.get("pm10")
        # pm2_5 = pm_data.get("pm25")

        print(f"도시 : {city}")
        print(f"기온: {temp}℃")
        print(f"체감온도: {sensible_temp}℃")
        print(f"습도: {humidity}%")
        print(f"날씨: {weather}")
        print(f"풍속: {wind}m/s")
        # print(f"PM10: {pm10} ㎍/m³")
        # print(f"PM2.5: {pm2_5} ㎍/m³")
        print()

def extract_eup_myeon_dong(addr):
    # 주소에서 읍/면/동 추출 (예: "서울특별시 강남구 역삼동" -> "역삼동")
    match = re.search(r'(\S+[읍면동])', addr)
    return match.group(1) if match else None

def get_weather_station_data():
    #기상청 관측소 정보를 얻는 함수
    df = pd.read_csv('기상청관측소.txt', sep='\t', header=None, encoding='utf-8')
    pd.set_option('display.max_rows', None)  # 모든 행 출력

    # 헤더 지정
    df.columns = [ '지점명', '지점주소' ]

    # 종료일이 비어있는(운영 중인) 관측소만 추출
    df_active = df[df['종료일'].isna() | (df['종료일'] == '')]

    # 지점명, 지점주소만 추출
    result = df_active[['지점명', '지점주소']].copy()

    result['읍면동'] = result['지점주소'].apply(extract_eup_myeon_dong)
    return result

def get_pm_stations_tm_x_y(umd_name):
    url = 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getTMStdrCrdnt'
    params = {
        'serviceKey': SERVICE_KEY2,
        'returnType': 'json',
        'numOfRows': '1000',
        'pageNo': '1',
        'umdName': umd_name
    }

    response = requests.get(url, params=params)

    try:
        data = response.json()
    except Exception as e:
        print(f"[ERROR] '{umd_name}' 응답이 JSON이 아닙니다.")
        return []

    items = data.get('response', {}).get('body', {}).get('items', [])

    results = []

    for item in items:
        addr = (item.get('sidoName'), item.get('sggName'), item.get('umdName'))
        tm_x_y = (item.get('tmX'), item.get('tmY'))
        results.append((addr, tm_x_y))
    
    return results

def print_filtered_pm_station_tm_coords_sido_sgg():
    df = get_weather_station_data()
    for idx, row in df.iterrows():
        umd = row['읍면동']
        addr_full = row['지점주소']
        if not umd or not addr_full:
            continue

        # 시도, 시군구 추출
        sido_match = re.search(r'([가-힣]+[특별광역]?[시도])', addr_full)
        sgg_match = re.search(r'([가-힣]+[구군시])', addr_full)
        sido = normalize_sido(sido_match.group(1)) if sido_match else ''
        sgg = sgg_match.group(1) if sgg_match else ''

        pm_candidates = get_pm_stations_tm_x_y(umd)
        filtered = []
        for addr_tuple, tm_x_y in pm_candidates:
            sido_pm, sgg_pm, umd_pm = addr_tuple
            # 시도, 시군구만 비교
            if (normalize_sido(sido_pm) == sido) and (sgg_pm == sgg) and (umd_pm == umd):
                filtered.append((addr_tuple, tm_x_y))

        if filtered:
            for addr_tuple, tm_x_y in filtered:
                print(f"관측소주소: {addr_full}, TM주소: {addr_tuple}, TM좌표: {tm_x_y}")
        else:
            print(f"[매칭없음] 관측소주소: {addr_full}")

print_filtered_pm_station_tm_coords_sido_sgg()

def pm_stations():
    url = 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getMsrstnList'
    params ={'serviceKey' : SERVICE_KEY2, 'returnType' : 'json', 'numOfRows' : '1000', 'pageNo' : '1', 'addr' : '거제시', 'stationName' : '' }

    response = requests.get(url, params=params)
    print(response.text)

    
    


