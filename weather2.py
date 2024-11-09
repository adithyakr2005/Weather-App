import time
import adafruit_dht
import board
import spidev
import sqlite3
import RPi.GPIO as GPIO  # Import GPIO library

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Define GPIO pins for controlling sensor power
DHT11_POWER_PIN = 26
MQ135_POWER_PIN = 23
SOIL_MOISTURE_POWER_PIN = 24
LDR_POWER_PIN = 25

# Set the GPIO pins as outputs
GPIO.setup(DHT11_POWER_PIN, GPIO.OUT)
GPIO.setup(MQ135_POWER_PIN, GPIO.OUT)
GPIO.setup(SOIL_MOISTURE_POWER_PIN, GPIO.OUT)
GPIO.setup(LDR_POWER_PIN, GPIO.OUT)

# Initialize the DHT11 sensor (Temp and Humidity), connected to GPIO22 (data)
dht_device = adafruit_dht.DHT11(board.D22)

# SPI setup for MCP3008 (for Gas, Soil Moisture, and Light sensors)
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

# SQLite3 setup: Create a connection and table if not exists
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        air_quality REAL,
        soil_moisture REAL,
        light_intensity REAL,
        temperature REAL,
        humidity REAL,
        timestamp TEXT
    )
''')
conn.commit()

# Function to read from MCP3008
def read_channel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Convert ADC value to voltage
def convert_volts(data, vref=3.3):
    return (data * vref) / 1023.0

# Function to get gas level (air quality)
def get_gas_data():
    gas_level = read_channel(0)
    return gas_level  # Return the raw value instead of text

# Function to get soil moisture
def get_soil_moisture():
    moisture_value = read_channel(1)  # Assuming soil sensor is on channel 1
    return moisture_value  # Return the raw value

# Function to get light level
def get_light_level():
    light_level = read_channel(2)  # Assuming light sensor is on channel 2
    return light_level  # Return the raw value

# Function to read temperature and humidity with error handling and retries
def read_temperature_humidity(retries=5):
    for _ in range(retries):
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity
            if temperature is not None and humidity is not None:
                return temperature, humidity
        except RuntimeError as error:
            print(f"Error reading DHT11 sensor: {error}. Retrying...")
            time.sleep(2)
        except Exception as error:
            print(f"Unhandled error: {error}")
            break
    print("Failed to read DHT11 sensor after retries.")
    return None, None

# Function to gather all sensor data
def get_all_sensor_data():
    # Power ON sensors
    GPIO.output(DHT11_POWER_PIN, GPIO.HIGH)
    GPIO.output(MQ135_POWER_PIN, GPIO.HIGH)
    GPIO.output(SOIL_MOISTURE_POWER_PIN, GPIO.HIGH)
    GPIO.output(LDR_POWER_PIN, GPIO.HIGH)

    # Wait for sensors to stabilize
    time.sleep(2)

    temp, humidity = read_temperature_humidity()
    gas_level = get_gas_data()
    moisture_value = get_soil_moisture()
    light_level = get_light_level()

    # Power OFF sensors after reading
    GPIO.output(DHT11_POWER_PIN, GPIO.LOW)
    GPIO.output(MQ135_POWER_PIN, GPIO.LOW)
    GPIO.output(SOIL_MOISTURE_POWER_PIN, GPIO.LOW)
    GPIO.output(LDR_POWER_PIN, GPIO.LOW)

    return {
        "Temperature (C)": temp,
        "Humidity (%)": humidity,
        "Gas Level": gas_level,
        "Soil Moisture": moisture_value,
        "Light Level": light_level
    }

# Function to save sensor data to SQLite database
def save_to_sqlite(data):
    try:
        cursor.execute('''
            INSERT INTO sensor_data (air_quality, soil_moisture, light_intensity, temperature, humidity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['Gas Level'],
            data['Soil Moisture'],
            data['Light Level'],
            data['Temperature (C)'],
            data['Humidity (%)'],
            time.strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
    except Exception as e:
        print(f"Failed to write to SQLite: {e}")

# Main loop to read sensor data and save to SQLite every 5 minutes
if __name__ == "__main__": 
    try:
        while True:
            # Gather sensor data
            sensor_data = get_all_sensor_data()

            # Save the data to SQLite database
            save_to_sqlite(sensor_data)
            print(f"Sensor data saved to SQLite: {sensor_data}")

            # Wait for 5 minutes (300 seconds)
            time.sleep(60)  # 5 minutes
    except KeyboardInterrupt:
        pass
    finally:
        try:
            dht_device.exit()
        except Exception as e:
            print(f"Error during DHT11 cleanup: {e}")
        spi.close()  # Close SPI connection
        conn.close()  # Close SQLite connection
        GPIO.cleanup()  # Clean up GPIO
