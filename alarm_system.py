def generate_alarms(weather_data_list):
    alarms = []

    for entry in weather_data_list:
        city = entry.get('city')
        hour = int(entry.get('hour')) if entry.get('hour') is not None else None
        temp = entry.get('temperature')
        try:
            temp = float(temp) if temp is not None else None
        except ValueError:
            temp = None
        wind_speed = entry.get('wind_speed')
        dust_avg = entry.get('dust_avg', 0)
        uv_index = entry.get('uv_index', 0)
        rainfall = entry.get('rainfall', 0)
        snowfall = entry.get('snowfall', 0)

        # 온도 경고
        if temp is not None:
            if temp >= 35:
                temp_warning = "폭염 경보 발령"
                temp_health_risk = "열사병, 열탈진에 주의하세요. 충분한 수분 섭취와 그늘에서의 휴식이 필요합니다."
            elif temp >= 33:
                temp_warning = "폭염 주의보 발령"
                temp_health_risk = "더운 날씨로 인해 열사병 위험이 있으니 무리한 야외활동을 자제하세요."
            elif temp <= -15:
                temp_warning = "한파 경보 발령"
                temp_health_risk = "저체온증, 동상 위험이 높습니다. 따뜻한 옷 착용과 외출 자제를 권장합니다."
            elif temp <= -12:
                temp_warning = "한파 주의보 발령"
                temp_health_risk = "한파로 인한 저체온증 위험이 있습니다. 노약자는 특히 주의하세요."
            else:
                temp_warning = None
                temp_health_risk = None
        else:
            temp_warning = None
            temp_health_risk = None

        # 강풍 경고
        if wind_speed is not None:
            if wind_speed >= 21:
                wind_warning = "강풍 경보 발령"
                wind_health_risk = "강풍으로 인해 피부 화상이나 이물질에 의한 부상 가능성이 있습니다. 보호 장비 착용을 권장합니다."
            elif wind_speed >= 14:
                wind_warning = "강풍 주의보 발령"
                wind_health_risk = "강한 바람으로 인한 외부 이물질 부상 주의가 필요합니다."
            else:
                wind_warning = None
                wind_health_risk = None
        else:
            wind_warning = None
            wind_health_risk = None

        # 미세먼지 및 황사 경고
        if dust_avg >= 800:
            dust_warning = "황사 경보 발령"
            dust_health_risk = "호흡기 질환 및 눈/피부 자극이 심할 수 있습니다. 외출을 자제하고 마스크 착용을 권장합니다."
        elif dust_avg >= 300:
            dust_warning = "미세먼지 경보 발령"
            dust_health_risk = "심장 및 폐 질환이 있는 사람은 특히 주의해야 합니다. 마스크 착용이 필요합니다."
        elif dust_avg >= 150:
            dust_warning = "미세먼지 주의보 발령"
            dust_health_risk = "어린이, 노인은 실외활동을 줄여주세요. 마스크 착용을 권장합니다."
        else:
            dust_warning = None
            dust_health_risk = None

        # 자외선 지수 경고
        if uv_index < 3:
            uv_status = "낮음"
            uv_warning = None
        elif uv_index < 6:
            uv_status = "보통"
            uv_warning = "햇볕에 장시간 노출되지 않도록 주의하세요. 자외선 차단제를 바르는 것이 좋습니다."
        elif uv_index < 8:
            uv_status = "높음"
            uv_warning = "햇볕에 노출 시 자외선 차단제를 사용하고, 모자나 선글라스를 착용하세요."
        elif uv_index < 11:
            uv_status = "매우 높음"
            uv_warning = "자외선 차단제를 꼭 사용하고 가능한 한 그늘에 머무르세요. 화상을 입을 수 있습니다."
        else:
            uv_status = "위험"
            uv_warning = "가능한 실외활동을 피하고, 자외선 차단제를 반드시 사용하세요. 피부 화상 위험이 매우 높습니다."

        # 강수량 경고
        if rainfall >= 90:
            rainfall_warning = "호우 경보 발령"
            rain_health_risk = "홍수 및 침수 위험이 높습니다. 안전한 장소로 대피하세요."
        elif rainfall >= 60:
            rainfall_warning = "호우 주의보 발령"
            rain_health_risk = "도로 침수 및 교통 혼잡이 예상됩니다. 안전에 유의하세요."
        else:
            rainfall_warning = None
            rain_health_risk = None

        # 적설량 경고
        if snowfall >= 20:
            snowfall_warning = "대설 경보 발령"
            snow_health_risk = "많은 눈으로 인해 교통사고 위험 및 낙상 주의가 필요합니다."
        elif snowfall >= 5:
            snowfall_warning = "대설 주의보 발령"
            snow_health_risk = "눈으로 인한 사고 위험이 있으니 주의하세요."
        else:
            snowfall_warning = None
            snow_health_risk = None

        # 경고가 하나도 없으면 일반 메시지 추가
        if all(warning is None for warning in [
            temp_warning, wind_warning, dust_warning, uv_warning, rainfall_warning, snowfall_warning]):
            alarm = {
                "general": {
                    "warning": "현재 특별한 경고가 없습니다.",
                    "health_risk": ""
                }
            }
        else:
            alarm = {
                "temperature": {
                    "warning": temp_warning,
                    "health_risk": temp_health_risk
                },
                "wind": {
                    "warning": wind_warning,
                    "health_risk": wind_health_risk
                },
                "dust": {
                    "warning": dust_warning,
                    "health_risk": dust_health_risk
                },
                "uv": {
                    "index": uv_index,
                    "status": uv_status,
                    "warning": uv_warning
                },
                "rainfall": {
                    "warning": rainfall_warning,
                    "health_risk": rain_health_risk
                },
                "snowfall": {
                    "warning": snowfall_warning,
                    "health_risk": snow_health_risk
                }
            }

        alarms.append({
            'city': city,
            'hour': hour,
            'alarm': alarm
        })

    return alarms

def summarize_alarm(alarm):
    # 경고가 없는 경우
    if "general" in alarm:
        return alarm["general"]["warning"]

    messages = []

    # 온도 경고 요약
    temp = alarm.get("temperature", {})
    if temp.get("warning"):
        messages.append(f"온도: {temp['warning']} ({temp['health_risk']})")

    # 강풍 경고 요약
    wind = alarm.get("wind", {})
    if wind.get("warning"):
        messages.append(f"바람: {wind['warning']} ({wind['health_risk']})")

    # 미세먼지/황사 경고 요약
    dust = alarm.get("dust", {})
    if dust.get("warning"):
        messages.append(f"미세먼지/황사: {dust['warning']} ({dust['health_risk']})")

    # 자외선 경고 요약
    uv = alarm.get("uv", {})
    if uv.get("warning"):
        messages.append(f"자외선 지수({uv.get('index', '')}): {uv['warning']}")

    # 강수량 경고 요약
    rainfall = alarm.get("rainfall", {})
    if rainfall.get("warning"):
        messages.append(f"강수량: {rainfall['warning']} ({rainfall['health_risk']})")

    # 적설량 경고 요약
    snowfall = alarm.get("snowfall", {})
    if snowfall.get("warning"):
        messages.append(f"적설량: {snowfall['warning']} ({snowfall['health_risk']})")

    # 메시지가 없으면 특별한 경고 없음
    if not messages:
        return "현재 특별한 경고가 없습니다."

    return " / ".join(messages)