import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

# Add the project directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings and modules from the project
from config.settings import *
from src.tuya_cloud_connect import TuyaDeviceManager
from src.database import MongoDBClient

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
