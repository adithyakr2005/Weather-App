import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()

# Query to select all data from the 'sensor_data' table
cursor.execute('SELECT * FROM sensor_data')

# Fetch all rows from the result
rows = cursor.fetchall()

# Check if any data is returned
if rows:
    for row in rows:
        print(row)  # Print each row (you can also format this as needed)
else:
    print("No data found.")

# Close the connection
conn.close()
