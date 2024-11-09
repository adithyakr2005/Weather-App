import gps
import time

# Create a GPS instance
session = gps.gps(mode=gps.WATCH_ENABLE)

while True:
    try:
        # Read GPS data
        report = session.next()
        
        # Only process GPS data
        if report['class'] == 'TPV':
            # Print latitude and longitude
            if hasattr(report, 'lat') and hasattr(report, 'lon'):
                print(f"Latitude: {report.lat}, Longitude: {report.lon}")
        
        # Sleep for a bit before reading again
        time.sleep(1)

    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
        break
