import os
import sys
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import threading
import time
from datetime import datetime, timedelta

# Add the project directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings and modules from the project
from config.settings import *
from src.tuya_cloud_connect import TuyaDeviceManager
from src.database import MongoDBClient

app = Flask(__name__)
load_dotenv()

# Retrieve API credentials from environment variables
API_REGION = os.getenv('API_REGION')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

def is_data_changed(db_client, device_id, new_status):
    try:
        latest_record = db_client.get_latest_record(device_id)
        return latest_record['result'] != new_status['result']
    except Exception as e:
        print(f"Error checking data change: {e}")
        return True

def database_update(db_client, device):
    while True:
        try:
            device_status = device.get_status()

            if is_data_changed(db_client, device.device_id, device):
                db_client.insert_data(device.device_id, device)
                print(f"Inserted new soil data: {device}")

            time.sleep(1)

        except Exception as e:
            print(f"Error in database update: {e}")

@app.route('/get_sensor_data', methods=['POST'])
def get_sensor_data():
    try:
        data = request.json
        api_region = data.get('API_REGION')
        api_key = data.get('API_KEY')
        api_secret = data.get('API_SECRET')
        device_id = data.get('DEVICE_ID')

        if not all([api_region, api_key, api_secret, device_id]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Initialize TuyaDeviceManager for each device
        device = TuyaDeviceManager(api_region, api_key, api_secret, device_id, '154.61.204.255')
        if device.get_properties()['success']:
            device_status = device.get_status()
            if device_status:
                return jsonify(device.get_status()), 200
            else:
                return jsonify({"error": "Can't get the sensors data."}), 404
        else:
            return jsonify({"error": "Can't connect to the device."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_command', methods=['POST'])
def send_command():
    try:
        data = request.json
        api_region = data.get('API_REGION')
        api_key = data.get('API_KEY')
        api_secret = data.get('API_SECRET')
        device_id = data.get('DEVICE_ID')
        command = data.get('COMMAND')

        if not all([api_region, api_key, api_secret, device_id]):
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Initialize TuyaDeviceManager for each device
        device = TuyaDeviceManager(api_region, api_key, api_secret, device_id, '154.61.204.255')
        if device.get_properties()['success']:
            if device.send_command(command)['success']:
                return jsonify({"message": "Command has been sent successfully."}), 200
            else:
                return jsonify({"error": "Can't send the command to the device.'."}), 404
        else:
            return jsonify({"error": "Can't connect to the device."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

