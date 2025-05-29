from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
# import time

def get_city_weather():
    url = "https://www.weather.go.kr/w/observation/land/city-obs.do"

    options = Options()
    #options.add_argument('--headless') # 창 안띄우고 실행
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

        temp = cols[4].text.strip() # 기온
        sensible_temp = cols[6].text.strip() # 체감온도
        humidity = cols[8].text.strip() # 습도
        #weather = cols[1].text.strip() # 날씨
        #wind = cols[?].text.strip() # 풍력

        print(f"도시 : {city}")
        print(f"기온: {temp}")
        print(f"체감온도: {sensible_temp}")
        print(f"습도: {humidity}")
      #print(f"날씨: {weather}")
        #print(f"풍속: {wind}")
        print()

get_city_weather()