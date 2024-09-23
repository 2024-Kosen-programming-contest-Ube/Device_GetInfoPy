import os
import time
import json
import threading
import schedule
from sensor import Sensor, setLEDColor

class DataLogger:
    def __init__(self, filename, save_interval, send_interval):
        self.filename = filename
        self.save_interval = save_interval
        self.send_interval = send_interval
        self.sensor = Sensor()

        # Schedule the periodic save task
        schedule.every(self.save_interval).seconds.do(self.save_data_periodically)

    def get_current_log_filename(self):
        # Ensure that the directory path is constructed correctly
        current_path = os.getcwd()
        log_directory = os.path.join(current_path, "datalog")
        log_file = time.strftime("%Y-%m-%d_data_log.txt")
        return os.path.join(log_directory, log_file)

    def save_to_file(self, data):
        try:
            filename = self.get_current_log_filename()
            directory = os.path.dirname(filename)

            # Debugging prints to verify directory and filename
            print(f"Saving to file: {filename}")
            print(f"Directory: {directory}")

            # Ensure the directory exists
            os.makedirs(directory, exist_ok=True)

            with open(filename, "a") as file:
                time_str = time.strftime("%Y-%m-%d-%H:%M:%S")
                file.write(f"{time_str} {json.dumps(data)}\n")
        except Exception as e:
            print(f"Error writing to file {filename}: {e}")

    def save_data_periodically(self):
        try:
            env_data = self.sensor.getEnviroment()
            print(f"Environment data: {env_data}")  # デバッグ用

            # エアコンデータの取得を確認
            air_data = self.sensor.getAirConditioner()
            print(f"Air conditioner data: {air_data}")  # デバッグ用
            temperature, humidity = env_data
            airconditioner, ontime = air_data
            data = {
                "temperature": temperature,
                "humidity": humidity,
                "isPeople": self.sensor.getMotion(),
                "lux": self.sensor.getLux(),
                "useairconditioner": airconditioner,
                "airconditioner_time": ontime
            }
            self.sensor.setBlinkLED(setLEDColor.YELLOW, int(5))
            self.save_to_file(data)
        except Exception as e:
            print(f"Exception in save_data_periodically: {e}")

    def start_periodic_saving(self):
        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(1)

        thread = threading.Thread(target=run_schedule)
        thread.daemon = True
        thread.start()
