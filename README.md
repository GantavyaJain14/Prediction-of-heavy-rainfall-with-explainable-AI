# SIH XAI Rainfall Prediction System

This project is an **Explainable AI (XAI)** based web application designed to predict high-impact rainfall events using **INSAT-3DR** satellite data. The system not only predicts whether a heavy rain event is likely, but also provides an *explainable* heatmap overlay to show which parts of the satellite image contributed most to the prediction.

## 🌟 Key Features

1.  **AI-Based Prediction**: Analyzes INSAT-3DR Level-2B Infrared (.h5) images to predict rainfall impact (Low, Moderate, High).
2.  **Explainable AI (XAI)**: Generates heatmaps (using LIME-inspired techniques) overlaid on the satellite imagery, highlighting the dense cloud structures driving the prediction.
3.  **Real-Time Context**: Integrates with the **OpenWeatherMap API** to fetch live weather conditions (Temperature, Humidity, Status) and a 9-hour Nowcast for New Delhi.
4.  **Live Monitor (Watch Folder)**: A dashboard feature that automatically scans the dataset directory for new satellite images every 10 seconds and updates the UI without manual refreshing.
5.  **Automated Data Fetching**: Includes an automated background scheduler that uses the official MOSDAC `mdapi.py` script to fetch new satellite data every hour, creating a fully hands-free real-time pipeline.

---

## 📂 Project Structure

```text
d:/Practice/xai/
│
├── app/
│   ├── app.py                 # Main Flask Application & Web Server
│   ├── templates/             # HTML Templates (index.html)
│   └── static/                # CSS/JS (if separated)
│
├── src/                       # Core Logic Modules
│   ├── insat_loader.py        # Reads and normalizes .h5 satellite data
│   ├── predictor.py           # Machine learning / thresholding prediction logic
│   ├── xai.py                 # Generates heatmaps for explainability
│   └── weather_client.py      # Fetches data from OpenWeatherMap API
│
├── mosdac_config.json         # (Deprecated) Original config name
├── config.json                # Credentials and parameters for MOSDAC mdapi
├── mdapi.py                   # Official ISRO/MOSDAC download script
├── daily_sync.py              # Wrapper script to update config.json with today's date
│
├── .env                       # Environment variables (OpenWeatherMap API Key)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🛠️ Prerequisites & Setup

### 1. Python Environment
Ensure you have Python 3.8+ installed. It is recommended to use a virtual environment.

```powershell
cd d:/Practice/xai
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. API Keys & .env
The system requires an OpenWeatherMap API key for live weather data.
Create a `.env` file in the root directory:
```
OPENWEATHER_API_KEY=your_api_key_here
```

### 3. MOSDAC Credentials (For Automation)
To automatically download new satellite images, you need a MOSDAC account.
Edit the `config.json` file in the root directory:
```json
"user_credentials": {
    "username/email": "your_mosdac_username",
    "password": "your_mosdac_password"
}
```

---

## 🚀 How to Run the Application

Start the Flask development server:
```powershell
python app/app.py
```
Open your browser and navigate to: **http://127.0.0.1:5000**

### 1. Manual Mode
- Select an existing `.h5` file from the dropdown menu on the left.
- Click **"Run Analysis"**.
- The system will process the image, generate the XAI heatmap, and display the prediction alongside live weather data.

### 2. Live Monitor Mode
- Click the **"🔴 Start Live Monitor"** button on the dashboard.
- The web app will start polling the backend every 10 seconds.
- Whenever a new `.h5` file is added to the `d:/Practice/xai` folder, the UI will automatically process and display it!

---

## 🔄 How the Automation Works

To simulate a real-time satellite feed, the system includes a background automation pipeline:

1.  **Background Scheduler**: When `app.py` is running, an `APScheduler` job runs every 60 minutes in the background.
2.  **Daily Sync (`daily_sync.py`)**: The scheduler calls this script. It dynamically updates `config.json` to search for satellite images from "Yesterday" to "Today".
3.  **MDAPI Downloader (`mdapi.py`)**: The sync script then executes the official MOSDAC downloader. It authenticates with your credentials, finds the latest `3RIMG_L2B_IMC` files, and downloads them.
4.  **UI Update**: Because the frontend "Live Monitor" is polling `app.py`, it instantly detects the newly downloaded file and updates the screen.

You can also trigger the download manually at any time by running:
```powershell
python daily_sync.py
```
