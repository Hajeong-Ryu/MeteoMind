import requests
from bs4 import BeautifulSoup
import time

def get_weather():
    sido = "경기도"
    sido_codes = {
        "서울": "1100000000",
        "경기도": "4100000000",
        "강원도": "5100000000",
        "충청북도": "4300000000",
        "충청남도": "4400000000",
        "전라북도": "5200000000",
        "전라남도": "4600000000",
        "경상북도": "4700000000",
        "경상남도": "4800000000",
        "제주도": "5000000000",
        "광주": "2900000000",
        "대구": "2700000000",
        "대전": "3000000000",
        "부산": "2600000000",
        "세종": "3600000000",
        "울산": "3100000000",
        "인천": "2800000000",
        "전국": "asos",
    }

    station_dict = {}

    db = "MINDB_01M" #관측 간격을 매분 마다로 설정
    tm = "" #현재 시간으로 설정
    stnid = "0" #지역번호
    sidoCode = sido_codes[sido] #시도코드번호

    #지역번호와 시도코드를 변경하여 원하는 지역으로 설정할 수 있음
    #기상청에 모든 지역이 존재하지 않아 기상청에 있는 지역만 가능

    url = f"https://www.weather.go.kr/w/observation/land/aws-obs.do?db={db}&tm={tm}&stnId={stnid}&sidoCode={sidoCode}"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.select_one("tbody")

    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 11:
            continue  # 데이터 누락 방지

        station_name = cols[1].text.strip()
        rainfall_indicator = cols[3].text.strip()
        rainfall_amount = cols[4].text.strip()
        temp = cols[5].text.strip()
        sensible_temp = cols[6].text.strip()
        wind_speed = cols[8].text.strip()
        humidity = cols[9].text.strip()

        station_dict[station_name] = {
            "기온(℃)": temp,
            "체감온도(℃)": sensible_temp,
            "강수유무": rainfall_indicator,
            "강수량": rainfall_amount,
            "풍속(m/s)": wind_speed,
            "습도(%)": humidity,
        }

    for name, info in station_dict.items():
        print(f"\n {name}")
        for key, value in info.items():
            print(f"   {key}: {value}")
    
    time.sleep(0.5)  # 서버 과부하 방지
    
get_weather()