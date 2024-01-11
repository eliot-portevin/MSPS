from datetime import datetime
from os.path import exists


class Logger:
    def __init__(self):
        self.date = datetime.now().strftime('%d-%m-%Y')
        self.log_file = f'{self.date}.log'
        self.initiate_log_file()

    def log(self, message):
        date = datetime.now().strftime('%H:%M:%S')
        message = f'[{date}] - {message}'

        with open(self.log_file, 'a') as f:
            f.write(message + '\n')

    def initiate_log_file(self):
        if not exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write('')