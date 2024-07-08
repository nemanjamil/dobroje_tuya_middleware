from tuya_cloud_connect import TuyaDeviceManager


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

if __name__ == "__main__":
    # Initialize the manager with your credentials
    irrig_controller = TuyaDeviceManager(
        api_region=API_REGION,
        api_key=API_KEY,
        api_secret=API_SECRET,
        api_device_id=DEVICES['Irrigation controller']
    )

    # Display properties of the device
    irrig_controller.get_device_logs()

    # Get device current status
    irrig_controller.get_status()

    # Get  device properties
    irrig_controller.get_properties()