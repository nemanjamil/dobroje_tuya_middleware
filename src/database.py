from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME, COLLECTION_NAME
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import json
import os
import sys

# Load environment variables from a .env file
load_dotenv()

# Retrieve API credentials from environment variables
mongo_user = os.getenv('mongo_user')
mongo_pass = os.getenv('mongo_pass')
mongo_cluster = os.getenv('mongo_cluster')
mongo_options = os.getenv('mongo_options')

class MongoDBClient:
    def __init__(self):
        uri = f"mongodb+srv://{mongo_user}:{mongo_pass}@{mongo_cluster}/{mongo_options}"        # Create a new client and connect to the server
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]

    def insert_data(self, device_name, data):
        try:
            if data is None or not data:
                print(f"No valid data available for {device_name}. Skipping insertion.")
                return

            result = self.collection.insert_one({
                "device_name": device_name,
                "timestamp": datetime.now(),
                "data": data
            })

        except Exception as e:
            print(f"Error inserting data to MongoDB: {e}")

    def get_data_by_device_name(self, device_name):
        try:
            results = self.collection.find({"device_name": device_name})
            return list(results)
        except Exception as e:
            print(f"Error retrieving data from MongoDB: {e}")
            return []

    def get_data_by_date_range(self, start_date, end_date):
        try:
            results = self.collection.find({
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            })
            return list(results)
        except Exception as e:
            print(f"Error retrieving data from MongoDB: {e}")
            return []

    def get_latest_record(self, device_name):
        try:
            result = self.collection.find_one(
                {"device_name": device_name},
                sort=[("timestamp", -1)]  # Sort by timestamp in descending order
            )
            return result['data']
        except Exception as e:
            print(f"Error retrieving latest data from MongoDB: {e}")
            return None
        
    def get_latest_results(self, device_name):
        try:
            result = self.collection.find_one(
                {"device_name": device_name},
                sort=[("timestamp", -1)]  # Sort by timestamp in descending order
            )
            data = result['data']['result']
            parsed_data = {item['code']: item['value'] for item in data}
            return parsed_data
        except Exception as e:
            print(f"Error retrieving latest data from MongoDB: {e}")
            return None


    def close(self):
        self.client.close()
