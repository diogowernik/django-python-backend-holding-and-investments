# utils.py
import csv
import os
from datetime import datetime

# Lista global para registrar erros
error_log = []

# Função para registrar erros
def log_error(message, event_type=None, event_date=None):
    error_entry = {
        'Error Message': message,
        'Event Type': event_type if event_type else 'N/A',
        'Event Date': event_date.strftime('%Y-%m-%d') if event_date else 'N/A'
    }
    error_log.append(error_entry)
    print(message)

def convert_to_datetime(date_str):
    if date_str is None:
        log_error("Data nula detectada")
        return None
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.replace(hour=18, minute=0, second=0)
    except ValueError:
        log_error(f"Falha ao converter a data: {date_str}")
        return None

PROCESSED_BATCHES_FILE = 'processed_batches.csv'

def read_processed_batches():
    if not os.path.exists(PROCESSED_BATCHES_FILE):
        return set()
    with open(PROCESSED_BATCHES_FILE, 'r') as csvfile:
        reader = csv.reader(csvfile)
        return set(row[0] for row in reader)

def write_processed_batch(batch_name):
    with open(PROCESSED_BATCHES_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([batch_name])

def write_error_log_to_csv(errors, batch_name):
    filename = f'error_log_{batch_name}.csv'
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Error Message', 'Event Type', 'Event Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for error in errors:
            writer.writerow(error)

def split_events_by_date(events_list, date_ranges):
    batches = []
    for start_date, end_date in date_ranges:
        batch = [event for event in events_list if start_date <= event['sort_date'] <= end_date]
        batches.append(batch)
    return batches
