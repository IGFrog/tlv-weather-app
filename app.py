from flask import Flask, render_template_string
import requests

app = Flask(__name__)

def get_rain_forecast():
    # Tel Aviv coordinates: 32.0853, 34.7818
    url = "https://api.open-meteo.com/v1/forecast?latitude=32.0853&longitude=34.7818&daily=rain_sum,precipitation_probability_max&timezone=auto"
    try:
        response = requests.get(url)
        data = response.json()
        
        # Get today's forecast
        today_rain = data['daily']['rain_sum'][0]
        today_prob = data['daily']['precipitation_probability_max'][0]
        
        return {
            'rain_sum': today_rain,
            'probability': today_prob,
            'will_rain': today_prob > 20 or today_rain > 0.5
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def index():
    forecast = get_rain_forecast()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌧️ Tel Aviv Rain Predictor</title>
        <style>
            body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f4f8; margin: 0; }
            .card { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; max-width: 400px; }
            h1 { color: #2c3e50; }
            .status { font-size: 1.5rem; margin: 20px 0; font-weight: bold; }
            .rainy { color: #3498db; }
            .dry { color: #f39c12; }
            .details { color: #7f8c8d; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Tel Aviv Weather</h1>
            {% if forecast.error %}
                <p style="color: red">Error fetching weather data</p>
            {% else %}
                <div class="status {% if forecast.will_rain %}rainy{% else %}dry{% endif %}">
                    {% if forecast.will_rain %}
                        🌧️ It might rain today!
                    {% else %}
                        ☀️ Likely no rain today.
                    {% endif %}
                </div>
                <div class="details">
                    <p>Precipitation Probability: {{ forecast.probability }}%</p>
                    <p>Expected Rain: {{ forecast.rain_sum }} mm</p>
                </div>
            {% endif %}
            <p style="font-size: 0.8rem; margin-top: 30px;">Artifacts stored in JFrog Artifactory</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, forecast=forecast)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

