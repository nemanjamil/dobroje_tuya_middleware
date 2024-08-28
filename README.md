# Tuya Device API

This project provides an API for interacting with Tuya devices, enabling you to retrieve sensor data and send commands using FastAPI.

## Features

- Retrieve sensor data from Tuya devices.
- Send commands to Tuya devices.
- Detailed Swagger documentation for API exploration.

## Requirements

- Python 3.7+
- FastAPI
- Pydantic
- Uvicorn
- python-dotenv

## Setup

### Clone the Repository

```bash
git clone https://github.com/your-username/tuya-device-api.git
cd tuya-device-api
```

## Install Dependencies

Ensure Python and pip are installed. Install dependencies with:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root with your weather API credentials:

```bash
WEATHER_API_KEY=6gqMZk48W7uyxPvLlZvbSAIxVxtMU6Ux
```

## Run the API

Start the FastAPI server using:
```bash
python app.py
```

# Usage
## Retrieving Sensor Data

Send a POST request to `/get_sensor_data` with JSON body:

```json
{
    "API_REGION": "your_api_region",
    "API_KEY": "your_api_key",
    "API_SECRET": "your_api_secret",
    "DEVICE_ID": "your_device_id"
}
```
Example Request:
```json
{
    "API_REGION": "eu",
    "API_KEY": "9u7uqwsp7u9pxkfmswae",
    "API_SECRET": "5479b5a39e464313911b4a41eb0c7355",
    "DEVICE_ID": "vdevo172072913903404"
}
```

## Sending a Command

Send a POST request to `/send_command` with JSON body:

```json
{
    "API_REGION": "your_api_region",
    "API_KEY": "your_api_key",
    "API_SECRET": "your_api_secret",
    "DEVICE_ID": "your_device_id",
    "COMMAND": {
        "commands": [
            {
                "code": "switch",
                "value": true
            }
        ]
    }
}
```

Example Request:
```json
{
    "API_REGION": "eu",
    "API_KEY": "x5xq5g4qht5pfvcakdvr",
    "API_SECRET": "34f89f40acdf4de6ae23e63eef181a16",
    "DEVICE_ID": "vdevo172044590691636",
    "COMMAND": {
        "commands": [
            {
                "code": "switch",
                "value": true
            }
        ]
    }
}
```

# Documentation

Access Swagger documentation at `http://127.0.0.1:8000/docs` for detailed API endpoint information and testing directly in your browser.
