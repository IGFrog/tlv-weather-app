from flask import Flask, render_template_string
import requests
import certifi

app = Flask(__name__)

def get_rain_forecast():
    # Tel Aviv coordinates: 32.0853, 34.7818
    url = "https://api.open-meteo.com/v1/forecast?latitude=32.0853&longitude=34.7818&daily=rain_sum,precipitation_probability_max&timezone=auto"
    try:
        # Verify=False to bypass local SSL issues
        response = requests.get(url, verify=False)
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
        <title>🌧️ Global Rain Radar & TLV Forecast</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        
        <!-- Leaflet CSS -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        
        <style>
            body { margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; }
            #map { height: 100vh; width: 100vw; z-index: 1; }
            
            .overlay-card {
                position: absolute;
                top: 20px;
                left: 20px;
                z-index: 1000;
                background: rgba(255, 255, 255, 0.85);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                padding: 2rem;
                border-radius: 20px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.18);
                max-width: 350px;
                text-align: center;
                transition: transform 0.3s ease;
            }
            
            .overlay-card:hover { transform: translateY(-5px); }
            
            h1 { margin-top: 0; color: #1a202c; font-size: 1.8rem; }
            .status { font-size: 1.4rem; margin: 15px 0; font-weight: 700; }
            .rainy { color: #3182ce; }
            .dry { color: #d69e2e; }
            
            .data-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-top: 15px;
                text-align: left;
            }
            
            .data-item {
                background: rgba(255,255,255,0.5);
                padding: 10px;
                border-radius: 10px;
            }
            
            .label { font-size: 0.8rem; color: #718096; display: block; margin-bottom: 4px; }
            .value { font-size: 1.1rem; font-weight: 600; color: #2d3748; }
            
            .footer { margin-top: 20px; font-size: 0.75rem; color: #718096; }
            
            /* Legend for Rain */
            .legend {
                position: absolute;
                bottom: 30px;
                right: 20px;
                z-index: 1000;
                background: rgba(0,0,0,0.7);
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 0.8rem;
            }
            .gradient-bar {
                width: 200px;
                height: 10px;
                background: linear-gradient(to right, transparent, #9BE2FE, #0043FE, #6900CC, #FF00C8);
                margin-top: 5px;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div id="map"></div>
        
        <div class="overlay-card">
            <h1>Tel Aviv Forecast</h1>
            {% if forecast.error %}
                <p style="color: #e53e3e">Error fetching local data</p>
            {% else %}
                <div class="status {% if forecast.will_rain %}rainy{% else %}dry{% endif %}">
                    {% if forecast.will_rain %}
                        🌧️ Rain Expected
                    {% else %}
                        ☀️ Clear Skies
                    {% endif %}
                </div>
                
                <div class="data-grid">
                    <div class="data-item">
                        <span class="label">Chance</span>
                        <span class="value">{{ forecast.probability }}%</span>
                    </div>
                    <div class="data-item">
                        <span class="label">Amount</span>
                        <span class="value">{{ forecast.rain_sum }} mm</span>
                    </div>
                </div>
            {% endif %}
            <div class="footer">
                Artifacts via JFrog Artifactory<br>
                Map data &copy; OpenStreetMap<br>
                Radar data &copy; RainViewer
            </div>
        </div>

        <div class="legend">
            Live Rain Intensity
            <div class="gradient-bar"></div>
            <div style="display: flex; justify-content: space-between; margin-top: 2px; font-size: 0.7rem;">
                <span>Light</span>
                <span>Heavy</span>
            </div>
        </div>

        <!-- Leaflet JS -->
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            // Initialize Map centered on Tel Aviv
            const map = L.map('map').setView([32.0853, 34.7818], 7);

            // Dark Mode Map Tiles (CartoDB Dark Matter)
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
                subdomains: 'abcd',
                maxZoom: 19
            }).addTo(map);

            // Add RainViewer Radar Layer
            // We fetch the latest available timestamp from RainViewer API first
            fetch('https://api.rainviewer.com/public/weather-maps.json')
                .then(response => response.json())
                .then(data => {
                    // Get the last available past frame (most recent radar data)
                    const latestFrame = data.radar.past[data.radar.past.length - 1];
                    const timestamp = latestFrame.time;
                    
                    // Add the tile layer
                    L.tileLayer(`https://tile.rainviewer.com${latestFrame.path}/256/{z}/{x}/{y}/2/1_1.png`, {
                        opacity: 0.8,
                        zIndex: 100
                    }).addTo(map);
                })
                .catch(err => console.error("Error loading radar:", err));

            // Add Marker for Tel Aviv
            L.marker([32.0853, 34.7818]).addTo(map)
                .bindPopup('<b>Tel Aviv</b><br>Our Location')
                .openPopup();
        </script>
    </body>
    </html>
    """
    return render_template_string(html, forecast=forecast)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
