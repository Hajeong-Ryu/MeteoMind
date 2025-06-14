from alarm_system import summarize_alarm

test_alarm = {
    "temperature": {"warning": None, "health_risk": None},
    "wind": {"warning": None, "health_risk": None},
    "dust": {"warning": None, "health_risk": None},
    "uv": {"index": 1, "status": "낮음", "warning": None},
    "rainfall": {"warning": None, "health_risk": None},
    "snowfall": {"warning": None, "health_risk": None},
}

result = summarize_alarm(test_alarm)
print("=== Test Result ===")
print(result)
