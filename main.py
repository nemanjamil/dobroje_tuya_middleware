from fastapi import FastAPI
from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routers import devices
from app.db.mongodb_client import MongoDBClient
from app.services.tuya_service import TuyaDeviceManager, start_device_threads


load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Tuya Device API",
    description="API for interacting with Tuya devices",
    version="1.0.0"
)

# Initialize database client
db_client = MongoDBClient()

# Device credentials (example, replace with actual data)
DEVICES = {
    "Irrigation controller": "vdevo172044590691636",
    "Luminance sensor": "vdevo172044570814122",
    "Smart soil sensor": "vdevo172044411129779"
}

# Initialize Tuya devices
devices = [
    TuyaDeviceManager(os.getenv('API_REGION'), os.getenv('API_KEY'), os.getenv('API_SECRET'), device_id)
    for device_id in DEVICES.values()
]

# Start threads for database updates
start_device_threads(db_client, devices)

# Include device router
app.include_router(devices.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
