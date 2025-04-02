import serial 
import time
import datetime
import csv
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Replace 'COM7' with the correct port where your Arduino is connected
serial_port = 'COM7'
baud_rate = 9600

# Initialize serial communication
ser = serial.Serial(serial_port, baud_rate, timeout=1)

# Get current date to use as the filename for the CSV
current_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
filename = f'{current_date}.csv'

# Initialize CSV file with headers
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Average Value (kg)'])

# Variable to track the maximum value recorded
max_value = float('-inf')

# Initialize data for plotting
timestamps = []
average_values = []

# Create an empty figure for real-time plotting
fig = make_subplots()
trace = go.Scatter(x=[], y=[], mode='lines', name='Average Value (kg)')
fig.add_trace(trace)

# Configure layout
fig.update_layout(title='Real-time Load Cell Data',
                  xaxis_title='Timestamp',
                  yaxis_title='Average Value (kg)',
                  xaxis_rangeslider_visible=True)

# Show the plot in browser
fig.show()

def read_and_average_values():
    values = []
    start_time = time.time()

    # Collect readings for 1 second (500ms intervals)
    while time.time() - start_time < 1:
        if ser.is_open and ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            try:
                value = float(line)
                values.append(value)
            except ValueError:
                print(f"Received non-numeric data: {line}")
        
        time.sleep(0.5)  # Wait 500 ms between readings

    # Calculate the average value
    if values:
        average_value = sum(values) / len(values)
        return average_value
    return None

def update_plot():
    global fig, timestamps, average_values
    fig.data[0].x = timestamps
    fig.data[0].y = average_values
    fig.show()

def main():
    global max_value
    # Allow time for Arduino to reset and establish communication
    time.sleep(2)

    try:
        while True:
            average_value = read_and_average_values()
            if average_value is not None:
                # Update the max_value if the new average is higher
                if average_value > max_value:
                    max_value = average_value

                timestamp = datetime.datetime.now().strftime('%H:%M:%S')
                print(f"{timestamp} Lettura media: {average_value:.2f} kg")

                # Save the result in the CSV file
                with open(filename, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, average_value])

                # Append data for plotting
                timestamps.append(timestamp)
                average_values.append(average_value)

                # Update the plot
                #update_plot()

            time.sleep(5)  # Poll every second for new average value

    except KeyboardInterrupt:
        # Save the maximum value before exiting
        print("\nProgramma interrotto. Salvando il valore massimo nel CSV...")
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Valore massimo registrato', max_value])
        
        print(f"Valore massimo registrato: {max_value:.2f} kg")
        ser.close()  # Close the serial connection before exiting
        exit()

if __name__ == "__main__":
    main()
