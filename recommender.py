def generate_recommendations(parsed_data):
    recommendations = []

    for entry in parsed_data:
        city = entry.get('city')
        hour = entry['hour']
        temp = entry['temperature']
        rain_type = entry['rain_type']
        humidity = entry['humidity']
        wind_speed = entry['wind_speed']

        # 의상 추천
        if temp >= 28:
            clothes = "민소매, 반팔, 반바지를 권장합니다."
        elif temp >= 23:
            clothes = "반팔, 얇은 셔츠를 착용하세요"
        elif temp >= 20:
            clothes = "긴팔, 얇은 겉옷을 착용하세요"
        elif temp >= 17:
            clothes = "가디건, 니트를 추천합니다."
        elif temp >= 12:
            clothes = "자켓, 얇은 코트를 착용하세요"
        elif temp >= 9:
            clothes = "트렌치코트, 두꺼운 니트를 착용하세요"
        elif temp >= 5:
            clothes = "코트, 가죽자켓, 히트텍 착용을 권장합니다."
        else:
            clothes = "패딩, 목도리, 장갑 등의 방한용품을 준비하세요."

        if rain_type in ['비', '비/눈', '눈']:
            clothes += " + 우산을 준비하세요."

        # 활동 추천
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

        # 외출 가능 여부
        if rain_type in ['비/눈', '눈'] or wind_speed >= 13 or temp < 0:
            going_out = "외출 비추천"
        else:
            going_out = "외출 가능"

        recommendations.append({
            'city': city,
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
