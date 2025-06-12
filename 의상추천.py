def generate_recommendations(parsed_data):
    recommendations = []

    for entry in parsed_data:
        hour = entry['hour']
        temp = entry['temperature']
        rain_type = entry['rain_type']
        humidity = entry['humidity']
        wind_speed = entry['wind_speed']

        # 1. 의상 추천
        if temp >= 28:
            clothes = "민소매, 반팔, 반바지"
        elif temp >= 23:
            clothes = "반팔, 얇은 셔츠"
        elif temp >= 20:
            clothes = "긴팔, 얇은 겉옷"
        elif temp >= 17:
            clothes = "가디건, 니트"
        elif temp >= 12:
            clothes = "자켓, 얇은 코트"
        elif temp >= 9:
            clothes = "트렌치코트, 두꺼운 니트"
        elif temp >= 5:
            clothes = "코트, 가죽자켓, 히트텍"
        else:
            clothes = "패딩, 목도리, 장갑 등 방한용품"

        # 우산 등 비 관련 추가
        if rain_type in ['비', '비/눈', '눈']:
            clothes += " + 우산 준비"

        # 2. 활동 추천
        if rain_type in ['비', '비/눈', '눈']:
            activity = "실내 활동 추천 (카페, 영화 등)"
        elif wind_speed >= 10:
            activity = "강풍 주의, 실내 활동 추천"
        elif humidity >= 85:
            activity = "습도 높음, 가볍게 산책 정도 추천"
        elif temp >= 23:
            activity = "야외활동 추천 (등산, 운동, 공원 산책 등)"
        elif temp >= 10:
            activity = "적당한 야외활동 가능 (산책, 카페 투어 등)"
        else:
            activity = "실내 활동 추천 (너무 추움)"

        # 3. 외출 여부 추천
        if rain_type in ['비/눈', '눈'] or wind_speed >= 13 or temp < 0:
            going_out = "외출 비추천"
        else:
            going_out = "외출 가능"

        # 결과 묶기
        recommendations.append({
            'hour': hour,
            'temperature': temp,
            'rain_type': rain_type,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'clothes': clothes,
            'activity': activity,
            'going_out': going_out
        })

    return recommendations
