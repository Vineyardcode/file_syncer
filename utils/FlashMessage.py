import time

class FlashMessage:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path

    def log(self, action, *info):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        info_str = ', '.join(str(arg) for arg in info)
        log_message = f"[{timestamp}] Action: {action}, Info: {info_str}\n"
        
        with open(self.log_file_path, 'a') as f:
            f.write(log_message)
        
        print(log_message)
