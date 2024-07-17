import os
import time
import json
import threading
from Config import Config
import sensor
class DataLogger:
    def __init__(self, filename, save_interval, send_interval):
        self.filename = filename
        self.save_interval = save_interval
        self.send_interval = send_interval
        self.last_save_time = 0
        self.last_send_time = 0
        self.sensor=sensor.Sensor()

    def get_current_log_filename(self):
        return time.strftime("./datalog/%Y-%m-%d_data_log.txt")

    def save_to_file(self, data):
        filename = self.get_current_log_filename()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "a") as file:
            time_str = time.strftime("%Y-%m-%d-%H:%M:%S")
            file.write(f"{time_str} {json.dumps(data)}\n")

    def save_data_periodically(self):
        
        data = {"temperature": 25.5, "humidity": 60, "isPeople": self.sensor.getMotion() , "lux":self.sensor.getLux()} 
        while True:
            self.save_to_file(data)
            time.sleep(self.save_interval)

    def start_periodic_saving(self):
        thread = threading.Thread(target=self.save_data_periodically)
        thread.daemon = True
        thread.start()

# Example usage
config = Config('config.txt')
logger = DataLogger("./datalog/data_log.txt", config.save_interval, config.send_interval)
logger.start_periodic_saving()
