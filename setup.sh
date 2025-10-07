#!/bin/bash
# Setup script for Instagram Follower Analyzer

set -e

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Chromium and Chromedriver (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt update
    sudo apt install -y chromium-browser chromium-chromedriver
fi

echo "Setup complete!"
echo "To run the app:"
echo "source venv/bin/activate && python webapp/app.py"
echo "Then open http://127.0.0.1:5000/ in your browser."
