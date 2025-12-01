from flask import Flask, render_template_string, jsonify
import requests
import certifi

app = Flask(__name__)

# List of major cities to check for rain
CITIES = [
    {"name": "Tel Aviv", "lat": 32.0853, "lon": 34.7818},
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "New York", "lat": 40.7128, "lon": -74.0060},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    {"name": "Singapore", "lat": 1.3521, "lon": 103.8198},
    {"name": "Sydney", "lat": 1.3521, "lon": 151.2093},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
    {"name": "Berlin", "lat": 48.8566, "lon": 13.4050},
    {"name": "Seattle", "lat": -33.8688, "lon": 151.2093},
]

def get_raining_cities():
    raining_cities = []
    try:
        # Bulk fetch current weather for all cities using Open-Meteo
        lats = ",".join([str(c['lat']) for c in CITIES])
        lons = ",".join([str(c['lon']) for c in CITIES])
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&current=rain,showers,precipitation&timezone=auto"
        
        response = requests.get(url, verify=False)
        data = response.json()
        
        # Open-Meteo returns a list of results if multiple coords are passed
        results = data if isinstance(data, list) else [data]
        
        for i, res in enumerate(results):
            current = res.get('current', {})
            # Check if any precipitation is happening
            is_raining = (current.get('rain', 0) > 0) or (current.get('showers', 0) > 0) or (current.get('precipitation', 0) > 0)
            
            if is_raining:
                city = CITIES[i].copy()
                city['rain_amount'] = current.get('precipitation', 0)
                raining_cities.append(city)
                
    except Exception as e:
        print(f"Error fetching city weather: {e}")
    
    return raining_cities

def get_rain_forecast():
    # Tel Aviv coordinates
    url = "https://api.open-meteo.com/v1/forecast?latitude=32.0853&longitude=34.7818&daily=rain_sum,precipitation_probability_max&timezone=auto"
    try:
        response = requests.get(url, verify=False)
        data = response.json()
        today_rain = data['daily']['rain_sum'][0]
        today_prob = data['daily']['precipitation_probability_max'][0]
        
        return {
            'rain_sum': today_rain,
            'probability': today_prob,
            'will_rain': today_prob > 20 or today_rain > 0.5
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/radar-timestamp')
def get_radar_timestamp():
    try:
        response = requests.get('https://api.rainviewer.com/public/weather-maps.json', verify=False)
        data = response.json()
        latest = data['radar']['past'][-1]
        return jsonify(latest)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    forecast = get_rain_forecast()
    raining_now = get_raining_cities()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌧️ Global Rain Radar</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            body { margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; overflow: hidden; }
            #map { height: 100vh; width: 100vw; z-index: 1; }
            
            .card {
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(10px);
                padding: 1.5rem;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);
                margin-bottom: 15px;
            }
            
            .sidebar {
                position: absolute;
                top: 20px;
                left: 20px;
                z-index: 1000;
                max-width: 320px;
                max-height: 90vh;
                overflow-y: auto;
            }
            
            h1 { margin: 0 0 10px 0; font-size: 1.5rem; color: #2d3748; }
            h2 { margin: 0 0 10px 0; font-size: 1.1rem; color: #4a5568; border-bottom: 1px solid #cbd5e0; padding-bottom: 5px; }
            
            .status { font-size: 1.2rem; font-weight: 700; color: #3182ce; }
            .dry { color: #d69e2e; }
            
            .city-list { list-style: none; padding: 0; margin: 0; }
            .city-item {
                padding: 8px 0;
                border-bottom: 1px solid #eee;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .city-item:hover { color: #3182ce; padding-left: 5px; }
            .city-item:last-child { border-bottom: none; }
            
            .rain-badge {
                background: #ebf8ff;
                color: #2b6cb0;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
            }
            
            .legend {
                position: absolute; bottom: 30px; right: 20px; z-index: 1000;
                background: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 8px; font-size: 0.8rem;
            }
            .gradient-bar {
                width: 200px; height: 10px;
                background: linear-gradient(to right, transparent, #9BE2FE, #0043FE, #6900CC, #FF00C8);
                margin-top: 5px; border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div id="map"></div>
        
        <div class="sidebar">
            <div class="card">
                <h1>Tel Aviv Forecast</h1>
                {% if forecast.error %}
                    <p style="color: red">Error fetching data</p>
                {% else %}
                    <div class="status {% if forecast.will_rain %}rainy{% else %}dry{% endif %}">
                        {% if forecast.will_rain %}🌧️ Rain Expected{% else %}☀️ Clear Skies{% endif %}
                    </div>
                    <p>Chance: {{ forecast.probability }}% | Vol: {{ forecast.rain_sum }}mm</p>
                {% endif %}
            </div>
            
            <div class="card">
                <h2>🌧️ Raining Now</h2>
                {% if raining_cities %}
                    <ul class="city-list">
                        {% for city in raining_cities %}
                        <li class="city-item" onclick="flyToCity({{ city.lat }}, {{ city.lon }}, '{{ city.name }}')">
                            <span>📍 {{ city.name }}</span>
                            <span class="rain-badge">{{ city.rain_amount }} mm</span>
                        </li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p style="color: #718096; font-size: 0.9rem;">No rain in major monitored cities right now.</p>
                {% endif %}
            </div>
        </div>

        <div class="legend">Live Radar<div class="gradient-bar"></div></div>

        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            const map = L.map('map').setView([32.0853, 34.7818], 4);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors',
                subdomains: 'abcd',
                maxZoom: 19
            }).addTo(map);

            // Add Radar
            fetch('/radar-timestamp')
                .then(r => r.json())
                .then(data => {
                    if(data.path) {
                        L.tileLayer(`https://tile.rainviewer.com${data.path}/256/{z}/{x}/{y}/2/1_1.png`, {
                            opacity: 0.8, zIndex: 100
                        }).addTo(map);
                    }
                });

            // Add markers for raining cities
            {% for city in raining_cities %}
                L.marker([{{ city.lat }}, {{ city.lon }}])
                 .addTo(map)
                 .bindPopup("<b>{{ city.name }}</b><br>Raining: {{ city.rain_amount }}mm");
            {% endfor %}
            
            // Tel Aviv Marker
            L.marker([32.0853, 34.7818]).addTo(map).bindPopup('<b>Tel Aviv</b>').openPopup();

            function flyToCity(lat, lon, name) {
                map.flyTo([lat, lon], 10, { duration: 2 });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, forecast=forecast, raining_cities=raining_now)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
