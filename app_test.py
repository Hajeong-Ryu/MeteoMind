from flask import Flask, render_template, request
from get_city_weather import get_weather_by_city
from recommender import generate_recommendations
from alarm_system import generate_alarms, summarize_alarm

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html") # index_html 불러오는 부분

@app.route("/result", methods=["POST"])
def result():
    city = request.form["city"]
    parsed_data = get_weather_by_city(city)
    if not parsed_data:
        return f"<h2>{city}에 대한 정보를 찾을 수 없습니다."
    recommendations = generate_recommendations(parsed_data)
    alarms = generate_alarms(parsed_data)
    summarized_alarms = []
    if alarms:
        for a in alarms:
            summarized = summarize_alarm(a['alarm'])
            summarized_alarms.append({
                'hour': a['hour'],
                'summary': summarized
            })
    else:
        summarized_alarms.append({
            'hour': '',
            'summary': "현재 특별한 경고가 없습니다."
        })
    return render_template("result.html", results=recommendations, city=city, alarms=summarized_alarms)
    
if __name__ == "__main__":
    app.run(debug=True)

