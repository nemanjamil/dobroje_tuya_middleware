import tinytuya
import socket
import requests
from ip2geotools.databases.noncommercial import DbIpCity
from geopy.distance import distance
from dotenv import load_dotenv
# Load environment variables from a .env file
load_dotenv()
import sys
import os
import pytz

# Add the project directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *
from urllib.parse import urlencode

# Retrieve API credentials from environment variables
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

class TuyaDeviceManager:
    def __init__(self, api_region, api_key, api_secret, api_device_id, ip=None):
        self.cloud = tinytuya.Cloud(
            apiRegion=api_region, 
            apiKey=api_key, 
            apiSecret=api_secret, 
            apiDeviceID=api_device_id
        )
        self.weather_api_key = WEATHER_API_KEY
        self.device_id = api_device_id
        self.ip = ip
        self.lon = None
        self.lat = None

        # Weather API Configuration 
        self.url = GET_TIMELINE_URL
        self.fields = FIELDS
        self.units = UNITS
        self.timesteps = TIMESTEPS
        self.timezone = TIMEZONE
        self.weather_api_key = WEATHER_API_KEY 

    def get_functions(self):
        result = self.cloud.getfunctions(self.device_id)
        functions = result['result']['functions']
        print("Functions of device:")
        for func in functions:
            print(f"  Code: {func['code']}")
            print(f"  Description: {func['desc']}")
            print(f"  Name: {func['name']}")
            print(f"  Type: {func['type']}")
            print(f"  Values: {func['values']}")
            print("")

    def get_location(self):
        try:
            if self.ip is not None:
                location = DbIpCity.get(self.ip, api_key="free")
                self._set_location(location)
                return location
            else:
                print("IP address isn't set")
                return None
        except Exception as e:
            print(f"Error in getting location: {e}")
            return None

    def _set_location(self, location):
        if location:
            self.lon = location.longitude
            self.lat = location.latitude

    def get_weather_data(self):
        if self.lon is None or self.lat is None:
            location = self.get_location()
            if location:
                self._set_location(location)
                print(f"Longitude: {self.lon}, Latitude: {self.lat}")
            else:
                print("Failed to get location")
                return None
        try:
            parameters = {
                "apikey": self.weather_api_key,
                "location": ','.join(map(str, [self.lat, self.lon])),
                "fields": ','.join(self.fields),
                "units": self.units,
                "timesteps": ','.join(self.timesteps),
                "timezone": self.timezone,
            }
            full_url = f"{self.url}?{urlencode(parameters)}"
            response = requests.get(full_url)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
        
    def send_command(self, commands):
        result = self.cloud.sendcommand(self.device_id, commands)
        if result['success']:
            return result
        else:
            print("Failed to send command")
            return None
        
    def get_device_information(self):
        return self.cloud.get_device_info(self.device_id)

    def get_devices_list(self):
        devices = self.cloud.getdevices()
        for device in devices:
            print(f"Name: {device['name']}")
            print(f"ID: {device['id']}")
            print(f"Key: {device['key']}")
            print(f"Category: {device['category']}")
            print(f"Product Name: {device['product_name']}")
            print(f"Product ID: {device['product_id']}")
            print(f"UUID: {device['uuid']}")
            print("")
        return devices

    def get_properties(self):
        result = self.cloud.getproperties(self.device_id)
        if result['success']:
            return result
        else:
            print("Failed to retrieve properties")
            return None

    def get_status(self):
        result = self.cloud.getstatus(self.device_id)
        return result

    def get_device_logs(self, start=None, end=None):
        result = self.cloud.getdevicelog(self.device_id, start=start, end=end)
        print("Device logs:")
        for log in result['result']['logs']:
            print(f"  Event Time: {log['event_time']}")
            if 'code' in log:
                print(f"  Code: {log['code']}")
            if 'value' in log:
                print(f"  Value: {log['value']}")
            print("")
