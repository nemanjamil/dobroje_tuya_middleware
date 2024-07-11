import sys
import os
from dotenv import load_dotenv
# Add the project directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings and modules from the project
from config.settings import *
from src.tuya_cloud_connect import TuyaDeviceManager

# Load environment variables from a .env file
load_dotenv()

# Retrieve API credentials from environment variables
API_REGION = os.getenv('API_REGION')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

# Initialize TuyaDeviceManager for each device
lumin_sensor = TuyaDeviceManager(API_REGION, API_KEY, API_SECRET, DEVICES['Luminance sensor'])
soil_sensor = TuyaDeviceManager(API_REGION, API_KEY, API_SECRET, DEVICES['Smart soil sensor'], '154.61.204.255')
irrigation_controller = TuyaDeviceManager(API_REGION, API_KEY, API_SECRET, DEVICES['Irrigation controller'])

# Call and print outputs for each function for lumin_sensor
print("Luminance Sensor:")
print(lumin_sensor.get_status())
lumin_sensor.get_functions()
lumin_sensor.get_devices_list()
lumin_sensor.get_properties()
lumin_sensor.get_device_logs()

# Call and print outputs for each function for soil_sensor
print("Smart Soil Sensor:")
print(soil_sensor.get_status())
print(soil_sensor.get_weather_data())
soil_sensor.get_functions()
soil_sensor.get_devices_list()
soil_sensor.get_properties()
soil_sensor.get_device_logs()

# Call and print outputs for each function for irrigation_controller
print("Irrigation Controller:")
print(irrigation_controller.get_status())
irrigation_controller.get_functions()
irrigation_controller.get_devices_list()
irrigation_controller.get_properties()
irrigation_controller.get_device_logs()