import sys
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import threading
import time

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

def is_data_changed(db_client, sensor_name, new_status):
    """
    Check if the new data differs from the latest data in the database.
    
    Args:
    db_client: Database client instance.
    sensor_name: Name of the sensor.
    new_status: New data from the sensor.
    
    Returns:
    bool: True if data has changed, False otherwise.
    """
    try:
        latest_record = db_client.get_latest_record(sensor_name)
        return latest_record['result'] != new_status['result']
    except Exception as e:
        print(f"Error checking data change: {e}")
        return True  # Assume data has changed if there's an error

def database_update(db_client, lumin_sensor, soil_sensor):
    """
    Continuously update the database with new sensor data if it has changed.
    
    Args:
    db_client: Database client instance.
    lumin_sensor: Luminance sensor instance.
    soil_sensor: Soil sensor instance.
    """
    while True:
        try:
            # Retrieve status from the sensors
            lumin_status = lumin_sensor.get_status()
            soil_status = soil_sensor.get_status()

            # Check if the luminance data has changed and update the database if it has
            if is_data_changed(db_client, 'Luminance sensor', lumin_status):
                db_client.insert_data('Luminance sensor', lumin_status)
                print(f"Inserted new luminance data: {lumin_status}")

            # Check if the soil data has changed and update the database if it has
            if is_data_changed(db_client, 'Smart soil sensor', soil_status):
                db_client.insert_data('Smart soil sensor', soil_status)
                print(f"Inserted new soil data: {soil_status}")

            # Wait for 1 second before the next iteration
            time.sleep(1)

        except Exception as e:
            print(f"Error in database update: {e}")

def auto_irrigation(db_client, irrigation_controller):
    """
    Automatically control irrigation based on sensor data.
    
    Args:
    db_client: Database client instance.
    irrigation_controller: Irrigation controller instance.
    """
    work_mode = None
    while True:
        try:
            # Get the current working mode of the irrigation controller (auto/manual)
            data = irrigation_controller.get_status()['result']
            parsed_data = {item['code']: item['value'] for item in data}
            work_mode = parsed_data['work_state']
            valve_state = parsed_data['switch']
            if work_mode == 'auto':
                # Get the latest soil sensor data from the database
                soil_sensor = db_client.get_latest_results('Smart soil sensor')

                # Turn on irrigation if soil temperature is high
                if soil_sensor['temp_current'] > 25 and valve_state == False:
                    print("Soil temperature is high. Turning on irrigation")
                    commands = {'commands': [{'code': 'switch', 'value': True}]}
                    irrigation_controller.send_command(commands)
                elif soil_sensor['temp_current'] <= 25 and valve_state == True:
                    print("Soil temperature is low. Turning off irrigation")
                    commands = {'commands': [{'code': 'switch', 'value': False}]}
                    irrigation_controller.send_command(commands)

            elif work_mode == 'manual':
                print("Irrigation controller is in manual mode")
            else:
                print("Unknown mode")

            # Wait for 1 second before the next iteration
            time.sleep(1)

        except Exception as e:
            print(f"Error in auto_irrigation: {e}")

if __name__ == "__main__":
    try:
        # Initialize TuyaDeviceManager for each device
        lumin_sensor = TuyaDeviceManager(API_REGION, API_KEY, API_SECRET, DEVICES['Luminance sensor'])
        soil_sensor = TuyaDeviceManager(API_REGION, API_KEY, API_SECRET, DEVICES['Smart soil sensor'])
        irrigation_controller = TuyaDeviceManager(API_REGION, API_KEY, API_SECRET, DEVICES['Irrigation controller'])

        # Initialize MongoDB client
        db_client = MongoDBClient()

        # Create threads for concurrent execution of database update and auto irrigation
        insert_thread = threading.Thread(target=database_update, args=(db_client, lumin_sensor, soil_sensor))
        record_thread = threading.Thread(target=auto_irrigation, args=(db_client, irrigation_controller))

        # Start the threads
        insert_thread.start()
        record_thread.start()

        # Join threads to ensure the main program waits for them to finish
        insert_thread.join()
        record_thread.join()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db_client.close()  # Close the database client when done
