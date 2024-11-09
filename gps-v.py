import serial

# Set up serial connection (check your /dev/serial port, usually ttyS0 or ttyAMA0)
ser = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=1)

while True:
    line = ser.readline().decode('ascii', errors='replace')
    if line.startswith('$GPGGA'):  # GPGGA sentence for latitude and longitude
        print(line)

