# 🌧️ Tel Aviv Rain Predictor & Global Radar

A Flask application that provides real-time rain forecasting for Tel Aviv and visualizes global precipitation using a weather radar map.

## 🌟 Features
- **Tel Aviv Forecast:** Real-time rain probability and expected rainfall using Open-Meteo API.
- **Global Radar:** Interactive Leaflet.js map with live radar overlay from RainViewer.
- **Glassmorphism UI:** Modern, responsive interface.

## 🚀 Running Locally

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App:**
   ```bash
   python3 app.py
   ```
   Open [http://127.0.0.1:8080](http://127.0.0.1:8080) in your browser.

## 📦 Building & Publishing (JFrog)

This project is integrated with the JFrog Platform for dependency management and artifact release.

### Prerequisites
- JFrog CLI (`jf`) configured with your platform.
- Virtual Repository: `tlv-pypi-virtual`
- Target Repository: `tlv-pypi-local`

### Build Pipeline
To run a full build cycle with dependency tracking and build info:

```bash
# 1. Set Build Variables
export BUILD_NAME="tlv-weather-build"
export BUILD_NUMBER="6" # Increment this for new builds

# 2. Collect Git Info
jf rt bag $BUILD_NAME $BUILD_NUMBER --project=tlvw

# 3. Collect Environment Variables
jf rt bce $BUILD_NAME $BUILD_NUMBER --project=tlvw

# 4. Install Dependencies (Force install to record in Build Info)
jf pip install -r requirements.txt --no-cache-dir --force-reinstall \
  --build-name=$BUILD_NAME --build-number=$BUILD_NUMBER --project=tlvw

# 5. Create Wheel Artifact
python3 setup.py bdist_wheel

# 6. Upload Artifact
jf rt u "dist/tlv_weather_app-*.whl" tlv-pypi-local \
  --build-name=$BUILD_NAME --build-number=$BUILD_NUMBER \
  --project=tlvw

# 7. Publish Build Info
jf rt bp $BUILD_NAME $BUILD_NUMBER --project=tlvw \
  --build-url="https://github.com/IGFrog/tlv-weather-app/actions"
```

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **Frontend:** HTML5, Leaflet.js, CSS3
- **Data:** Open-Meteo, RainViewer, OpenStreetMap
