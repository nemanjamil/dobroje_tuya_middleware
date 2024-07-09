import tinytuya

class TuyaDeviceManager:
    def __init__(self, api_region, api_key, api_secret, api_device_id):
        self.cloud = tinytuya.Cloud(
            apiRegion=api_region, 
            apiKey=api_key, 
            apiSecret=api_secret, 
            apiDeviceID=api_device_id
        )
        self.device_id = api_device_id

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

    def data_receive(self):
        self.cloud.receive()

    def send_command(self, commands):
        result = self.cloud.sendcommand(self.device_id, commands)

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
