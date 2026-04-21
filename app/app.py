import os
import sys

# Add parent directory to path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, jsonify
import db as auth_db
from src.insat_loader import load_satellite_image
from src.predictor import predict_impact
from src.xai import generate_heatmap
from src.weather_client import get_current_weather, get_forecast
import traceback
import os
from apscheduler.schedulers.background import BackgroundScheduler
import daily_sync

app = Flask(__name__)

# Initialise the SQLite database and create tables
auth_db.init_db()

# --- Automation Scheduler ---
def start_scheduler():
    try:
        scheduler = BackgroundScheduler()
        # Run the sync task every 60 minutes
        scheduler.add_job(func=daily_sync.run_full_sync, trigger="interval", minutes=60)
        scheduler.start()
        print("⏰ [System] Background Scheduler Started: Will fetch MOSDAC data every 60 mins.")
    except Exception as e:
        print(f"Scheduler Error: {e}")

start_scheduler()
# ----------------------------

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Existing Datasets (Hardcoded for demo availability)
DATASET_DIR = "d:/Practice/xai/data/mosdac"
os.makedirs(DATASET_DIR, exist_ok=True)

# --- State Configuration ---
# Maps a User-Selected State to its Weather City and approximate Pixel Bounding Box 
# Bounding Box Format: (y_min, y_max, x_min, x_max) relative to 2816x2805 array
STATE_CONFIGS = {
    "All India": {"city": "New Delhi", "bounds": None},
    "Andhra Pradesh": {"city": "Amaravati", "bounds": (1400, 1900, 1100, 1500)},
    "Arunachal Pradesh": {"city": "Itanagar", "bounds": (800, 1100, 1800, 2300)},
    "Assam": {"city": "Dispur", "bounds": (900, 1200, 1700, 2100)},
    "Bihar": {"city": "Patna", "bounds": (900, 1200, 1300, 1600)},
    "Chhattisgarh": {"city": "Raipur", "bounds": (1200, 1600, 1100, 1500)},
    "Goa": {"city": "Panaji", "bounds": (1500, 1700, 800, 1000)},
    "Gujarat": {"city": "Ahmedabad", "bounds": (1000, 1600, 600, 1200)},
    "Haryana": {"city": "Chandigarh", "bounds": (700, 1000, 1000, 1300)},
    "Himachal Pradesh": {"city": "Shimla", "bounds": (500, 800, 1100, 1400)},
    "Jammu and Kashmir": {"city": "Srinagar", "bounds": (300, 700, 900, 1300)},
    "Jharkhand": {"city": "Ranchi", "bounds": (1100, 1400, 1300, 1600)},
    "Karnataka": {"city": "Bengaluru", "bounds": (1400, 1900, 800, 1200)},
    "Kerala": {"city": "Thiruvananthapuram", "bounds": (1800, 2300, 1000, 1300)},
    "Ladakh": {"city": "Leh", "bounds": (200, 600, 1100, 1600)},
    "Madhya Pradesh": {"city": "Bhopal", "bounds": (1000, 1500, 1000, 1500)},
    "Maharashtra": {"city": "Mumbai", "bounds": (1300, 1800, 800, 1300)},
    "Manipur": {"city": "Imphal", "bounds": (1000, 1300, 1900, 2200)},
    "Meghalaya": {"city": "Shillong", "bounds": (1000, 1200, 1700, 1900)},
    "Mizoram": {"city": "Aizawl", "bounds": (1200, 1400, 1900, 2100)},
    "Nagaland": {"city": "Kohima", "bounds": (900, 1100, 1900, 2200)},
    "Odisha": {"city": "Bhubaneswar", "bounds": (1200, 1600, 1300, 1700)},
    "Punjab": {"city": "Chandigarh", "bounds": (600, 900, 900, 1200)},
    "Rajasthan": {"city": "Jaipur", "bounds": (700, 1300, 600, 1100)},
    "Sikkim": {"city": "Gangtok", "bounds": (800, 1000, 1500, 1700)},
    "Tamil Nadu": {"city": "Chennai", "bounds": (1700, 2200, 1100, 1500)},
    "Telangana": {"city": "Hyderabad", "bounds": (1300, 1600, 1100, 1400)},
    "Tripura": {"city": "Agartala", "bounds": (1100, 1300, 1800, 2000)},
    "Uttar Pradesh": {"city": "Lucknow", "bounds": (800, 1300, 1100, 1600)},
    "Uttarakhand": {"city": "Dehradun", "bounds": (600, 900, 1200, 1500)},
    "West Bengal": {"city": "Kolkata", "bounds": (1100, 1500, 1500, 1800)},
    "Andaman and Nicobar Islands": {"city": "Port Blair", "bounds": (2000, 2500, 1800, 2200)},
    "Lakshadweep": {"city": "Kavaratti", "bounds": (2000, 2300, 600, 900)},
    "Chandigarh": {"city": "Chandigarh", "bounds": (600, 800, 1000, 1200)},
    "Delhi": {"city": "New Delhi", "bounds": (800, 1000, 1100, 1300)},
    "Puducherry": {"city": "Pondicherry", "bounds": (1700, 1900, 1200, 1400)},
    "Dadra and Nagar Haveli and Daman and Diu": {"city": "Daman", "bounds": (1200, 1400, 700, 900)}
}

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

# ------------------------------------------------------------------
# Auth API endpoints  (called by the frontend via fetch)
# ------------------------------------------------------------------

@app.route('/api/signup', methods=['POST'])
def api_signup():
    """
    Expects JSON: { "name": "...", "email": "...", "password": "..." }
    Returns JSON: { "success": true } | { "success": false, "error": "..." }
    """
    data = request.get_json(force=True)
    name     = (data.get('name', '') or '').strip()
    email    = (data.get('email', '') or '').strip()
    password = (data.get('password', '') or '').strip()

    if not name or not email or not password:
        return jsonify({'success': False, 'error': 'All fields are required.'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters.'}), 400

    result = auth_db.register_user(name, email, password)
    status = 201 if result['success'] else 409
    return jsonify(result), status


@app.route('/api/signin', methods=['POST'])
def api_signin():
    """
    Expects JSON: { "email": "...", "password": "..." }
    Returns JSON: { "success": true, "user": {...} } | { "success": false, "error": "..." }
    """
    data = request.get_json(force=True)
    email    = (data.get('email', '') or '').strip()
    password = (data.get('password', '') or '').strip()

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required.'}), 400

    result = auth_db.verify_user(email, password)
    status = 200 if result['success'] else 401
    return jsonify(result), status


@app.route('/')
def index():
    # List available H5 files for quick selection
    h5_files = [f for f in os.listdir(DATASET_DIR) if f.endswith('.h5')]
    states = list(STATE_CONFIGS.keys())
    return render_template('index.html', h5_files=h5_files, states=states)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        filename = request.form.get('filename')
        state_key = request.form.get('state', 'All India')
        state_info = STATE_CONFIGS.get(state_key, STATE_CONFIGS['All India'])
        
        if filename:
            # Use existing file
            filepath = os.path.join(DATASET_DIR, filename)
        else:
            # Handle Upload (Optional for now)
            file = request.files.get('file')
            if file and file.filename.endswith('.h5'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
            else:
                return jsonify({'error': 'No file selected'}), 400

        # 1. Load Data
        norm_data, raw_data = load_satellite_image(filepath)
        
        # Crop data if a specific state is selected
        bounds = state_info['bounds']
        if bounds:
            y_min, y_max, x_min, x_max = bounds
            # Ensure bounds are within array limits
            y_min, y_max = max(0, y_min), min(norm_data.shape[0], y_max)
            x_min, x_max = max(0, x_min), min(norm_data.shape[1], x_max)
            norm_data = norm_data[y_min:y_max, x_min:x_max]
            raw_data = raw_data[y_min:y_max, x_min:x_max]
        
        # 2. Predict
        prediction = predict_impact(raw_data)
        
        # 3. Generate XAI Visualization
        heatmap_base64 = generate_heatmap(norm_data)
        
        # 4. Get Current Weather (Context) & Forecast (Nowcast)
        city = state_info['city']
        live_weather = get_current_weather(city) 
        forecast = get_forecast(city)
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'image_data': heatmap_base64,
            'live_weather': live_weather,
            'forecast': forecast,
            'state_city': city
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/latest_analysis', methods=['GET'])
def latest_analysis():
    """
    Automatically finds the newest .h5 file in the directory and runs analysis.
    Useful for 'Live Monitor' or 'Watch Folder' mode.
    """
    try:
        state_key = request.args.get('state', 'All India')
        state_info = STATE_CONFIGS.get(state_key, STATE_CONFIGS['All India'])
        
        # 1. Find newest file by parsing datetime from filename
        # Filename format: 3RIMG_11MAR2026_0515_L2B_IMC_V01R00.h5
        files = [os.path.join(DATASET_DIR, f) for f in os.listdir(DATASET_DIR) if f.endswith('.h5')]
        if not files:
            return jsonify({'success': False, 'error': 'No .h5 files found'}), 404
            
        from datetime import datetime
        def extract_time(filepath):
            try:
                # Extracts '11MAR2026_0515'
                fname = os.path.basename(filepath)
                date_str = fname.split('_')[1] + '_' + fname.split('_')[2]
                return datetime.strptime(date_str, "%d%b%Y_%H%M")
            except:
                return datetime.min

        newest_file = max(files, key=extract_time)
        filename = os.path.basename(newest_file)
        
        # 2. Run Analysis
        norm_data, raw_data = load_satellite_image(newest_file)
        
        # Crop data if a specific state is selected
        bounds = state_info['bounds']
        if bounds:
            y_min, y_max, x_min, x_max = bounds
            y_min, y_max = max(0, y_min), min(norm_data.shape[0], y_max)
            x_min, x_max = max(0, x_min), min(norm_data.shape[1], x_max)
            norm_data = norm_data[y_min:y_max, x_min:x_max]
            raw_data = raw_data[y_min:y_max, x_min:x_max]
            
        prediction = predict_impact(raw_data)
        heatmap_base64 = generate_heatmap(norm_data)
        
        city = state_info['city']
        live_weather = get_current_weather(city) 
        forecast = get_forecast(city)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'prediction': prediction,
            'image_data': heatmap_base64,
            'live_weather': live_weather,
            'forecast': forecast,
            'state_city': city
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
