import csv
from datetime import datetime

class MockParallelPort:
    def __init__(self, log_file='trigger_log.csv'):
        self.log_file = log_file
        # Create or overwrite the CSV file and write the header
        with open(self.log_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Trigger Value'])  # Header row
    
    def setData(self, value):
        '''Simulate sending a trigger by logging the value and timestamp to the CSV file.'''
        timestamp = datetime.now().isoformat()  # Current time in ISO format
        with open(self.log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, value])  # Append the data

if __name__ == "__main__":
    mock_port = MockParallelPort()
 
    mock_port.setData(1)  # Trigger value 1
    mock_port.setData(255)  # Trigger value 255