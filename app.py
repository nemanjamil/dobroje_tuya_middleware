import os
import sys
import threading
import time
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import Dict, Any

# Add the project directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings and modules from the project
from config.settings import *
from src.tuya_cloud_connect import TuyaDeviceManager
from src.database import MongoDBClient

app = FastAPI()
load_dotenv()

# Retrieve API credentials from environment variables
API_REGION = os.getenv('API_REGION')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

class SensorDataRequest(BaseModel):
    API_REGION: str
    API_KEY: str
    API_SECRET: str
    DEVICE_ID: str

class CommandRequest(BaseModel):
    API_REGION: str
    API_KEY: str
    API_SECRET: str
    DEVICE_ID: str
    COMMAND: Dict[str, Any]

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

@app.post("/get_sensor_data")
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

@app.post("/send_command")
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
                return {"message": "Command has been sent successfully."}
            else:
                raise HTTPException(status_code=404, detail="Can't send the command to the device.")
        else:
            raise HTTPException(status_code=500, detail="Can't connect to the device.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)