import tinytuya

# Project credentials
API_REGION = "eu"
API_KEY="x5xq5g4qht5pfvcakdvr"
API_SECRET="34f89f40acdf4de6ae23e63eef181a16"

# Device credentials
DEVICES = {
    "Irrigation controller": "vdevo172044590691636",
    "Luminance sensor": "vdevo172044570814122",
    "Smart soil sensor": "vdevo172044411129779"
}

class TuyaDeviceManager:
    def __init__(self, api_region, api_key, api_secret, api_device_id):
        self.cloud = tinytuya.Cloud(
            apiRegion=api_region, 
            apiKey=api_key, 
            apiSecret=api_secret, 
            apiDeviceID=api_device_id
        )
        self.device_id = api_device_id

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
            properties = result['result']
            print(f"Category: {properties['category']}")
            for status in properties['status']:
                print(f"  Code: {status['code']}")
                print(f"  Name: {status['name']}")
                print(f"  Type: {status['type']}")
                print(f"  Values: {status['values']}")
                print("")
        else:
            print("Failed to retrieve properties")

    def get_status(self):
        result = self.cloud.getstatus(self.device_id)
        print("Status of device:")
        for status in result['result']:
            print(f"  {status['code']}: {status['value']}")

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

if __name__ == "__main__":
    # Initialize the manager with your credentials
    smart_soil = TuyaDeviceManager(
        api_region="eu",
        api_key="x5xq5g4qht5pfvcakdvr",
        api_secret="34f89f40acdf4de6ae23e63eef181a16",
        api_device_id=DEVICES['Smart soil sensor']
    )
    
    # Display properties of the device
    smart_soil.get_device_logs()

    # Get device current status
    smart_soil.get_status()

    # Get  device properties
    smart_soil.get_properties()


