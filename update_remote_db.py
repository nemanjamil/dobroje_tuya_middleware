import os
import sys
from fastapi import FastAPI, HTTPException
import threading
import time
import requests
import json
import http.client

# Add the project directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings and modules from the project
from config.settings import *
from src.tuya_cloud_connect import TuyaDeviceManager
from src.database import MongoDBClient

# Set the environment variable
ENV = os.getenv('ENV', 'development')

# Define the API URL based on the environment
if ENV == 'production':
    API_URL = "https://dobroje.rs/parametri.php?action=tuyaDevicesList"
    ENDPOINT_HOST = "dobroje.rs"
else:
    API_URL = "http://localhost/parametri.php?action=tuyaDevicesList"
    ENDPOINT_HOST = "localhost"

def is_data_changed(db_client, device_id, new_status):
    """
    Check if the new data differs from the latest data in the database.
    
    Args:
    db_client: Database client instance.
    device_id: ID of the device.
    new_status: New data from the sensor.
    
    Returns:
    bool: True if data has changed, False otherwise.
    """
    try:
        latest_record = db_client.get_latest_record(device_id)
        return latest_record['result'] != new_status['result']
    except Exception as e:
        print(f"Error checking data change: {e}")
        return True  # Assume data has changed if there's an error

def send_data_to_endpoint(device_id, data):
    """
    Send data to a specific endpoint.
    
    Args:
    device_id: ID of the device.
    data: Data to be sent.
    """
    conn = http.client.HTTPConnection(ENDPOINT_HOST)

    payload = json.dumps({
        "deviceID": device_id,
        "data": data
    })
    headers = {
        'Content-Type': 'application/json'
    }
    print(f"Payload: {payload}")
    try:
        conn.request("POST", "/parametri.php?action=tuyapayload", payload, headers)
        response = conn.getresponse()
        
        if response.status == 200:
            print(f"Successfully sent data for device: {device_id}")
        else:
            print(f"Failed to send data for device: {device_id}, status code: {response.status}")
            response_content = response.read().decode()
            print(response_content)
            
    except Exception as e:
        print(f"Error sending data to endpoint: {e}")
    finally:
        conn.close()

def database_update(db_client, device):
    """
    Continuously update the database with new device data if it has changed.
    
    Args:
    db_client: Database client instance.
    device: Device instance.
    """
    while True:
        try:
            # Retrieve status from the sensors
            device_status = device.get_status()
            # Check if the luminance data has changed and update the database if it has
            if is_data_changed(db_client, device.device_id, device_status):
                db_client.insert_data(device.device_id, device_status)
                print(f"Inserted new data for device: {device.device_id}: {device_status}")
                send_data_to_endpoint(device.device_id, device_status)

            # Wait for 1 second before the next iteration
            time.sleep(1)

        except Exception as e:
            print(f"Error in database update: {e}")

if __name__ == "__main__":
    import uvicorn
    
    db_client = MongoDBClient()
    response = requests.get(API_URL)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch devices")

    devices_data = response.json()

    devices = []

    # Iterate over each project
    for project in devices_data.get("projects", []):
        api_region = project.get("api_region")
        api_key = project.get("api_key")
        api_secret = project.get("api_secret")
        print(f"API Region: {api_region}, API Key: {api_key}, API Secret: {api_secret}")

        for device_name, device_id in project.get("devices", {}).items():
            print(f"Device Name: {device_name}, Device ID: {device_id}")
            device_manager = TuyaDeviceManager(api_region, api_key, api_secret, device_id)
            devices.append(device_manager)

    # Create threads for concurrent execution of database update for each device
    threads = []
    for device in devices:
        thread = threading.Thread(target=database_update, args=(db_client, device))
        threads.append(thread)
        thread.start()

    # Join threads to ensure the main program waits for them to finish
    for thread in threads:
        thread.join()
