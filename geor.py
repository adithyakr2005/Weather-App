import serial
import time

# Initialize serial connection to the GPS module (default baud rate is 9600)
gps_serial = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)

def parse_gps_data(data):
    if data.startswith('$GPGGA'):
        parts = data.split(',')
        if parts[2] and parts[4]:  # Check for valid latitude and longitude
            latitude = convert_gps(parts[2], parts[3])  # Convert latitude
            longitude = convert_gps(parts[4], parts[5])  # Convert longitude
            print(f"Latitude: {latitude}, Longitude: {longitude}")

def convert_gps(value, direction):
    degrees = float(value[:2])
    minutes = float(value[2:]) / 60
    decimal = degrees + minutes
    if direction == 'S' or direction == 'W':
        decimal *= -1
    return decimal

# Main loop to read data from the GPS module
try:
    while True:
        gps_data = gps_serial.readline().decode('utf-8', errors='ignore').strip()
        parse_gps_data(gps_data)
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
finally:
    gps_serial.close()
