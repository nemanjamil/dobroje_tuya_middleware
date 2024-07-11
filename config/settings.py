MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'sensorDB'
COLLECTION_NAME = 'sensorData'

# Device credentials
DEVICES = {
    "Irrigation controller": "vdevo172044590691636",
    "Luminance sensor": "vdevo172044570814122",
    "Smart soil sensor": "vdevo172044411129779"
}

# Weather API configuration
GET_TIMELINE_URL = "https://api.tomorrow.io/v4/timelines"
FIELDS = [
    "precipitationIntensity",
    "precipitationType",
    "windSpeed",
    "windGust",
    "windDirection",
    "temperature",
    "temperatureApparent",
    "cloudCover",
    "cloudBase",
    "cloudCeiling",
    "weatherCode",
]
UNITS = "imperial"
TIMESTEPS = ["current"]
TIMEZONE = "America/New_York"