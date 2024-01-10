from datetime import datetime


class Logger:
    def __init__(self):
        self.log_file = 'StreamingService.log'
        self.clear_log()

    def log(self, message):
        date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        message = f'[{date}] - {message}'

        with open(self.log_file, 'a') as f:
            f.write(message + '\n')

    def clear_log(self):
        with open(self.log_file, 'r') as f:
            lines = f.readlines()

        if len(lines) > 1000:
            with open(self.log_file, 'w') as f:
                f.writelines(lines[500:])