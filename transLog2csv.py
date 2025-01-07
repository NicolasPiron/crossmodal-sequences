import csv
import re

log_file_path = '/Users/pironn/Documents/PhD/experiment/crossmodal-sequences/data/output/sub-00/sub-00_run-01_cmseq-logs-20250107-1740.log'

# Output CSV file path
csv_output_path = '/Users/pironn/Documents/PhD/experiment/crossmodal-sequences/data/output/sub-00/logs_transformed.csv'

# Regex pattern to extract timestamp, log level, and message from each log entry
log_pattern = r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) - (?P<log_level>\w+) - (?P<message>.+)$'

# List to hold parsed log entries
parsed_logs = []

# Parse the log file and extract relevant fields
with open(log_file_path, 'r') as file:
    for line in file:
        match = re.match(log_pattern, line.strip())
        if match:
            parsed_logs.append(match.groupdict())

enhanced_logs = []

for log in parsed_logs:
    message = log['message']
    if ':' in message:
        name, value = map(str.strip, message.split(':', 1))
    else:
        name, value = message, ''

    enhanced_logs.append({
        'Timestamp': log['timestamp'],
        'Log Level': log['log_level'],
        'Name': name,
        'Value': value
    })

#
with open(csv_output_path, 'w', newline='') as csvfile:
    fieldnames = ['Timestamp', 'Log Level', 'Name', 'Value']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write header
    writer.writeheader()

    # Write log entries with enhanced structure
    for log in enhanced_logs:
        writer.writerow(log)
