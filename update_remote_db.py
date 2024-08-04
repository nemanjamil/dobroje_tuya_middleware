import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import threading
import time
import requests
from dotenv import load_dotenv
import json
import http.client

# Add the project directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings and modules from the project
from config.settings import *
from src.tuya_cloud_connect import TuyaDeviceManager
from src.database import MongoDBClient

# Load environment variables from a .env file
load_dotenv()

# Retrieve API credentials from environment variables
API_REGION = os.getenv('API_REGION')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

app = FastAPI(
    title="Tuya Device API",
    description="API for interacting with Tuya devices",
    version="1.0.0"
)

class SensorDataRequest(BaseModel):
    API_REGION: str = Field(..., description="API region for Tuya", example="eu")
    API_KEY: str = Field(..., description="API key for Tuya", example="9u7uqwsp7u9pxkfmswae")
    API_SECRET: str = Field(..., description="API secret for Tuya", example="5479b5a39e464313911b4a41eb0c7355")
    DEVICE_ID: str = Field(..., description="Device ID of the Tuya device", example="vdevo172072913903404")

class MultiSensorDataRequest(BaseModel):
    API_REGION: str = Field(..., description="API region for Tuya", example="eu")
    API_KEY: str = Field(..., description="API key for Tuya", example="9u7uqwsp7u9pxkfmswae")
    API_SECRET: str = Field(..., description="API secret for Tuya", example="5479b5a39e464313911b4a41eb0c7355")
    DEVICE_ID: List[str] = Field(..., description="Device IDs of the Tuya devices", example=["vdevo172044590691636", "vdevo172044570814122"])

class CommandRequest(BaseModel):
    API_REGION: str = Field(..., description="API region for Tuya", example="eu")
    API_KEY: str = Field(..., description="API key for Tuya", example="x5xq5g4qht5pfvcakdvr")
    API_SECRET: str = Field(..., description="API secret for Tuya", example="34f89f40acdf4de6ae23e63eef181a16")
    DEVICE_ID: str = Field(..., description="Device ID of the Tuya device", example="vdevo172044590691636")
    COMMAND: Dict[str, Any] = Field(..., description="Command to send to the Tuya device", example={
        "commands": [
            {
                "code": "switch",
                "value": True
            }
        ]
    })

@app.post("/get_sensor_data", summary="Get Sensor Data", description="Retrieve sensor data from a Tuya device")
async def get_sensor_data(request: SensorDataRequest):
    try:
        api_region = request.API_REGION
        api_key = request.API_KEY
        api_secret = request.API_SECRET
        device_id = request.DEVICE_ID

        # Initialize TuyaDeviceManager for each device
        device = TuyaDeviceManager(api_region, api_key, api_secret, device_id, '154.61.204.255')
        if device.get_properties()['success']:
            device_status = device.get_status()
            if device_status:
                return device_status
            else:
                raise HTTPException(status_code=404, detail="Can't get the sensors data.")
        else:
            raise HTTPException(status_code=500, detail="Can't connect to the device.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_multi_sensor_data", summary="Get Sensor Data", description="Retrieve sensor data from Tuya devices")
async def get_multi_sensor_data(request: MultiSensorDataRequest):
    try:
        api_region = request.API_REGION
        api_key = request.API_KEY
        api_secret = request.API_SECRET
        device_ids = request.DEVICE_ID

        all_device_status = {}

        for device_id in device_ids:
            # Initialize TuyaDeviceManager for each device
            device = TuyaDeviceManager(api_region, api_key, api_secret, device_id, '154.61.204.255')
            if device.get_properties()['success']:
                device_status = device.get_status()
                if device_status:
                    all_device_status[device_id] = device_status
                else:
                    all_device_status[device_id] = "Can't get the sensors data."
            else:
                all_device_status[device_id] = "Can't connect to the device."

        return all_device_status

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/send_command", summary="Send Command", description="Send a command to a Tuya device")
async def send_command(request: CommandRequest):
    try:
        api_region = request.API_REGION
        api_key = request.API_KEY
        api_secret = request.API_SECRET
        device_id = request.DEVICE_ID
        command = request.COMMAND

        # Initialize TuyaDeviceManager for each device
        device = TuyaDeviceManager(api_region, api_key, api_secret, device_id, '154.61.204.255')
        if device.get_properties()['success']:
            if device.send_command(command)['success']:
                return device.get_status()
            else:
                raise HTTPException(status_code=404, detail="Can't send the command to the device.")
        else:
            raise HTTPException(status_code=500, detail="Can't connect to the device.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    conn = http.client.HTTPConnection("dobroje.rs")
    
    payload = json.dumps({
        "deviceID": device_id,
        "data": data
    })
    headers = {
        'Content-Type': 'application/json'
    }

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
    
    # Initialize TuyaDeviceManager for each device
    devices = [
        TuyaDeviceManager(API_REGION, API_KEY, API_SECRET, DEVICES['Irrigation controller']),
        TuyaDeviceManager(API_REGION, API_KEY, API_SECRET, DEVICES['Luminance sensor']),
        TuyaDeviceManager(API_REGION, API_KEY, API_SECRET, DEVICES['Smart soil sensor'])
    ]

    # Create threads for concurrent execution of database update for each device
    threads = []
    for device in devices:
        thread = threading.Thread(target=database_update, args=(db_client, device))
        threads.append(thread)
        thread.start()

    # Join threads to ensure the main program waits for them to finish
    for thread in threads:
        thread.join()
