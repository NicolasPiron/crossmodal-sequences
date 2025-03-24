import csv
import re

def extract_log_info(log_fn):
    ''' Extracts the log entries from a log file and returns them as a list of dictionaries.
    Each dictionary contains the following fields:
    - Timestamp
    - Log Level
    - Name
    - Value
    '''
    # regular expression pattern for parsing the log file
    log_pattern = r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) - (?P<log_level>\w+) - (?P<message>.+)$'
    # Parse the log file and extract relevant fields
    parsed_logs = []
    with open(log_fn, 'r') as file:
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

    return enhanced_logs
    
def write_log_info_csv(enhanced_logs, out_fn):
    ''' Writes the log entries to a CSV file.'''

    with open(out_fn, 'w', newline='') as csvfile:
        fieldnames = ['Timestamp', 'Log Level', 'Name', 'Value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header
        writer.writeheader()
        # Write log entries with enhanced structure
        for log in enhanced_logs:
            writer.writerow(log)

block = 1
first_block = block - 1
print(first_block )
n_blocks = 4 - first_block 
print(n_blocks)

for i in range(first_block+1, n_blocks+1):
    print(i)