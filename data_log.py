import os
import time
import json
import threading
from Config import Config
import sensor
from sensor import Sensor,setLEDColor

class DataLogger:
    def __init__(self, filename, save_interval, send_interval):
        self.filename = filename
        self.save_interval = save_interval
        self.send_interval = send_interval
        self.last_save_time = 0
        self.last_send_time = 0
        self.sensor = sensor.Sensor()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def get_current_log_filename(self):
        return os.path.join(self.base_dir, time.strftime("datalog/%Y-%m-%d_data_log.txt"))

    def save_to_file(self, data):
        try:
            filename = self.get_current_log_filename()
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "a") as file:
                time_str = time.strftime("%Y-%m-%d-%H:%M:%S")
                file.write(f"{time_str} {json.dumps(data)}\n")
        except Exception as e:
            print(f"Error writing to file {filename}: {e}")

    def save_data_periodically(self):
        while True:
            try:
                temperature, humidity = self.sensor.getEnviroment()
                data = {
                    "temperature": temperature,
                    "humidity": humidity,
                    "isPeople": self.sensor.getMotion(),
                    "lux": self.sensor.getLux()
                }
                self.sensor.setBlinkLED(setLEDColor.YELLOW, 5.0)
                self.save_to_file(data)
                time.sleep(self.save_interval)
            except Exception as e:
                print(f"Exception in save_data_periodically: {e}")


    def start_periodic_saving(self):
        thread = threading.Thread(target=self.save_data_periodically)
        thread.daemon = True
        thread.start()