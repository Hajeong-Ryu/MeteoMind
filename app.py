from flask import Flask, render_template, request
from get_city_weather import get_weather_by_city
from recommender import generate_recommendations

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
    return render_template("result.html", results=recommendations, city=city)
    
if __name__ == "__main__":
    app.run(debug=True)

