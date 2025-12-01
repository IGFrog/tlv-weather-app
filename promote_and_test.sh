#!/bin/bash
set -e

export BUILD_NAME="tlv-weather-build"
export BUILD_NUMBER="9"
PROJECT_KEY="tlvw"

echo "🚀 Starting Build Lifecycle #$BUILD_NUMBER..."

# 1. Build & Publish (DEV)
echo "📦 Building and Publishing to Dev..."
python3 setup.py bdist_wheel
jf rt bag $BUILD_NAME $BUILD_NUMBER --project=$PROJECT_KEY
jf rt bce $BUILD_NAME $BUILD_NUMBER --project=$PROJECT_KEY
jf pip install -r requirements.txt --no-cache-dir --force-reinstall --build-name=$BUILD_NAME --build-number=$BUILD_NUMBER --project=$PROJECT_KEY
jf rt u "dist/tlv_weather_app-1.0.8*.whl" tlv-pypi-local --build-name=$BUILD_NAME --build-number=$BUILD_NUMBER --server-id=my-jfrog --project=$PROJECT_KEY
jf rt bp $BUILD_NAME $BUILD_NUMBER --server-id=my-jfrog --project=$PROJECT_KEY --build-url="http://localhost/ci/9"

# 2. Promotion
echo "🔼 Promoting Build #$BUILD_NUMBER to Staging..."
jf rt bpr $BUILD_NAME $BUILD_NUMBER tlv-pypi-staging-local \
    --status="STAGED" \
    --source-repo="tlv-pypi-local" \
    --comment="Promoted for integration testing" \
    --copy=true \
    --project=$PROJECT_KEY \
    --server-id=my-jfrog

echo "✅ Build Promoted to 'tlv-pypi-staging-local'"

# 3. Staging Tests
echo "🧪 Running Staging Tests..."
pip install pytest
export PYTHONPATH=$PYTHONPATH:.
pytest -v -s tests/

echo "🎉 Tests Passed! Ready for Production."
