# This recommendation of activitys is based on the weather conditions.
'''
    총 작성되는 함수는 5개, 
    시간대별 기온 분석, 의상 추천, 야외활동/실내활동 추천, 사용자 일정 입력

    사용자가 일정을 입력하면 해당 일정에 맞는 날씨를 추천해주는 프로그램
    가급적 사용자의 일정을 피해 활동을 추천해준다.

    시간대별 활동 추천 -> 사용자의 일정과 날씨 등을 기반으로 활동을 추천하
    시간대별로 기상 요소를 종합적으로 분석


'''

import requests
import json
import beautiful as soup

def get_weater_data(city_name, api_key):
    city_name = input("Enter city name: ")

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None
    
def display_weather(data):
    if data:
        city = data['name']
        country = data['sys']['country']
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']

        print(f"City: {city}, Country: {country}")
        print(f"Temperature: {temperature}°C")
        print(f"Weather: {weather_description.capitalize()}")
    else:
        print("City not found or API request failed.")

def recommend_activity(weather_description):
    if "clear" in weather_description:
        return "It's a great day for a walk or a picnic!"
    elif "cloud" in weather_description:
        return "How about visiting a museum or going to the cinema?"
    elif "rain" in weather_description:
        return "Perfect time for indoor activities like reading or cooking."
    elif "snow" in weather_description:
        return "Great day for skiing or building a snowman!"
    else:
        return "Enjoy your day, whatever the weather!"
    

def recommend_outfit(temperature):
    if temperature < 0: # 기온이 낮을 때 
        return "장갑, 모자, 두꺼운 외투와 두꺼운 바지를 입는 것이 좋습니다."
    elif 0 <= temperature < 15:
        return "얇은 자켓과 긴바지를 입는 것이 좋습니다."
    elif 15 <= temperature < 25:
        return "반팔 티셔츠와 반바지, 또는 얇은 바지를 입는 것이 좋습니다."
    elif 25 <= temperature < 35:
        return "반팔 티셔츠 또는 나시, 반바지를 입는 것이 좋습니다."
    

def anyalize_weather_data(data):
    temperature_tag = soup.find("span", string="기온")  # "기온"이라는 텍스트를 찾음
    print(temperature_tag.text)  # 실제 텍스트 출력