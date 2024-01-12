from datetime import datetime
import os

class Logger:
    LOGS_DIRECTORY = 'logs'

    def __init__(self):
        self.date = datetime.now().strftime('%d-%m-%Y')
        self.log_file = os.path.join(self.LOGS_DIRECTORY, f'{self.date}.log')
        self.initiate_log_file()

    @classmethod
    def current_timestamp(cls):
        return datetime.now().strftime('%H:%M:%S')

    def log(self, message):
        timestamp = self.current_timestamp()
        log_entry = f'[{timestamp}] - {message}'

        try:
            with open(self.log_file, 'a') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f'Error writing to log file: {e}')

    def initiate_log_file(self):
        try:
            os.makedirs(self.LOGS_DIRECTORY, exist_ok=True)
        except Exception as e:
            print(f'Error creating log directory: {e}')