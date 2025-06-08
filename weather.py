from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import urllib.parse
# import time

def get_city_weather():
    url = "https://www.weather.go.kr/w/observation/land/city-obs.do"

    options = Options()
    options.add_argument('--headless') # 창 안띄우고 실행
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

    rows = table.find_all("tr")[1:] # 0번째는 header이므로 1번째부터 추출


    for row in rows:
        city = row.find("th").text.strip() # 도시 이름
        cols = row.find_all("td")
        if len(cols) < 10: continue

        weather = cols[0].text.strip() # 날씨
        temp = cols[4].text.strip() # 기온
        sensible_temp = cols[6].text.strip() # 체감온도
        humidity = cols[8].text.strip() # 습도
        wind = cols[10].text.strip() # 풍속

        print(f"도시 : {city}")
        print(f"기온: {temp}℃")
        print(f"체감온도: {sensible_temp}℃")
        print(f"습도: {humidity}%")
        print(f"날씨: {weather}")
        print(f"풍속: {wind}m/s")
        print()

def check_risk(temp, humidity):
    if temp < 0 and humidity > 80:
        return "동파 위험"
    elif temp > 30 and humidity < 30:
        return "열사병 위험"
    elif temp > 35 and humidity < 50:
        return "폭염 경고"
    elif temp < 10 and humidity > 90:
        return "저체온증 위험"
    elif temp > 40 and humidity < 20:
        return "고온 건조 경고"
    elif temp < 20 and humidity > 70:
        return "감기 위험"
    else:
        return "위험 없음"

def get_pm():
    url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty'

    params = {
    'serviceKey': 'KH5Jlc6te5pGBhMfqRKnpxz6EO/5mwdKBNo+rEpnBvbb+bh/dHQklTCzNKLWfdvq25SI93ImU7QbHg8GA4Jv6Q==',
    'returnType': 'json',
    'numOfRows': '100',
    'pageNo': '1',
    'sidoName': '서울',
    'ver': '1.0'
    }

    response = requests.get(url, params=params)
    print(response.text)


get_pm()
