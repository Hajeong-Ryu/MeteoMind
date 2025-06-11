from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re

#일일 횟수 제한이 끝났을때 변경해서 사용
SERVICE_KEY = "KH5Jlc6te5pGBhMfqRKnpxz6EO/5mwdKBNo+rEpnBvbb+bh/dHQklTCzNKLWfdvq25SI93ImU7QbHg8GA4Jv6Q=="
SERVICE_KEY2 = "ODyQFTdVk9FRQzWddNBQa/3GaxSl6mr+3xef7rM5v5IzNXxB1eVBDTql2a+ONM9krccUP0RBIyX+XLITm9jKGQ=="
SERVICE_KEY3 = "m8phIfnGb0sGF6Z2uz6bScSiENtALCEKYxPfz2Af9ZdfT0cVRAJRhRnFpH0uQkjLatM7OY7Js37PT8IM1cq8xQ=="

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
    #시도명 표준화하는 함수
    for key, value in SIDO_NORMALIZE.items():
        if key in sido:
            return value
    return sido  # 매칭 안되면 원본 반환

def extract_eup_myeon_dong(addr):
    # 주소에서 읍/면/동 추출 (예: "서울특별시 강남구 역삼동" -> "역삼동")
    match = re.search(r'(\S+[읍면동가])', addr)
    return match.group(1) if match else None

def split_address(addr_full):

    # 시도 추출
    sido_match = re.match(r'([가-힣]+[특별광역]?[시도])\s+', addr_full)
    sido = sido_match.group(1) if sido_match else ''
    remain = addr_full[sido_match.end():] if sido_match else addr_full

    # 읍면동 추출 (마지막에 위치)
    umd_match = re.search(r'(\S+[읍면동가])$', remain)
    umd = umd_match.group(1) if umd_match else ''
    sgg = remain[:umd_match.start()].strip() if umd_match else remain.strip()

    return sido, sgg, umd

def get_weather_station_data():
    # 기상청 관측소 정보를 얻는 함수
    df = pd.read_csv('기상청관측소.txt', sep='\t', header=0, encoding='utf-8')
    pd.set_option('display.max_rows', None)  # 모든 행 출력

    # 헤더 지정 (종료일 컬럼이 없으므로 지점명, 지점주소만)
    # df.columns = ['지점명', '지점주소']  # header=0이면 필요 없음

    # 종료일 컬럼이 없으므로 전체 사용
    result = df[['지점명', '지점주소']].copy()
    result['읍면동'] = result['지점주소'].apply(extract_eup_myeon_dong)
    return result

def get_stations_tm_x_y(umd_name):
    url = 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getTMStdrCrdnt'
    params = {
        'serviceKey': SERVICE_KEY3,
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
        results.append((
            item.get('sidoName'), 
            item.get('sggName'), 
            item.get('umdName'),
            item.get('tmX'), 
            item.get('tmY')
        ))
    
    return results

def match_station_tm_coords(save_path="matched_tm_coords.csv"):
    # 기상청 관측소의 주소와 TM좌표API에서 얻은 주소를 매칭하는 함수

    df = get_weather_station_data()
    results = []
    for idx, row in df.iterrows():
        addr_full = row['지점주소']
        station_name = row['지점명']  # 지점명 추가
        # split_address 함수로 시도, 시군구, 읍면동 추출
        sido, sgg, umd = split_address(addr_full)
        if not umd or not addr_full:
            continue

        pm_candidates = get_stations_tm_x_y(umd)
        filtered = []
        for sido_name, sgg_name, umd_name, tm_x, tm_y in pm_candidates:
            # 시도, 시군구, 읍면동 모두 비교 (normalize_sido로 표준화)
            if (normalize_sido(sido_name) == normalize_sido(sido)) and (sgg_name == sgg) and (umd_name == umd):
                filtered.append((tm_x, tm_y))

        if filtered:
            for tm_x, tm_y in filtered:
                results.append({
                    "지점명": station_name,
                    "주소": addr_full,
                    "TM좌표": (tm_x, tm_y)
                })
        else:
            results.append({
                "지점명": station_name,
                "주소": addr_full,
                "TM좌표": None
            })

    pd.DataFrame(results).to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"저장 완료: {save_path}")
    return results

def get_nearest_pm_station(station, tm_x, tm_y):
    #기상청 관측소의 TM좌표를 기준으로 가장가까운 미세먼지 관측소의 관측소명을 얻는 함수
    url = 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList'

    params = {
        'serviceKey': SERVICE_KEY3,
        'returnType': 'json',
        'tmX': tm_x,
        'tmY': tm_y
    }

    response = requests.get(url, params=params)
    try:
        data = response.json()
        items = data.get('response', {}).get('body', {}).get('items', [])

        results = []
        if items:
            # 가장 가까운 측정소명 반환
            pm_station_name = items[0].get('stationName')
            results.append((station, pm_station_name))  # 튜플로 append
            return results
        else:
            return None
    except Exception as e:
        print(f"[ERROR] TM좌표({tm_x}, {tm_y}) 응답이 JSON이 아닙니다.")
        return None
    
def get_pm_values_by_station(station_name):
    url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty'
    params = {
        'serviceKey': SERVICE_KEY3,
        'returnType': 'json',
        'numOfRows': '1',
        'pageNo': '1',
        'stationName': station_name,
        'dataTerm': 'DAILY',
        'ver': '1.3'
    }
    response = requests.get(url, params=params)
    try:
        data = response.json()
        items = data.get('response', {}).get('body', {}).get('items', [])
        if items:
            pm10 = items[0].get('pm10Value')
            pm25 = items[0].get('pm25Value')
            return pm10, pm25
        else:
            return None, None
    except Exception as e:
        print(f"[ERROR] '{station_name}' 응답이 JSON이 아닙니다.")
        return None, None
    
def get_city_weather():
    # 기상청 도시별관측정보와 미세먼지 정보를 출력하는 함수
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

    # 관측소 주소 데이터프레임 준비
    station_df = get_weather_station_data()
    tm_coords = match_station_tm_coords()  # TM좌표 매칭 결과 리스트

    # TM좌표 매칭 결과를 dict로 변환 (지점명 → TM좌표)
    tm_dict = {item['지점명']: item['TM좌표'] for item in tm_coords if item['TM좌표'] is not None}

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

        # TM좌표 얻기
        tm = tm_dict.get(city)
        pm10, pm25 = None, None
        if tm:
            tm_x, tm_y = tm
            nearest = get_nearest_pm_station(city, tm_x, tm_y)
            if nearest and len(nearest) > 0:
                pm_station_name = nearest[0][1]
                pm10, pm25 = get_pm_values_by_station(pm_station_name)
            else:
                pm10, pm25 = None, None
        else:
            pm10, pm25 = None, None

        print(f"도시 : {city}")
        print(f"기온: {temp} ℃")
        print(f"체감온도: {sensible_temp} ℃")
        print(f"습도: {humidity} %")
        print(f"날씨: {weather}")
        print(f"풍속: {wind} m/s")
        print(f"미세먼지: {pm10 if pm10 else '정보없음'} ㎍/m³")
        print(f"초미세먼지: {pm25 if pm25 else '정보없음'} ㎍/m³")
        print()
