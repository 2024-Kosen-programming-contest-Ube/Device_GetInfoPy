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
        return os.path.join("/home/pi/Device_GetInfoPy", time.strftime("datalog/%Y-%m-%d_data_log.txt"))

    def save_to_file(self, data):
        print("do")
        try:
            filename = self.get_current_log_filename()
            print(f"Saving to file: {filename}")
            directory = os.path.dirname(filename)
            print(f"Creating directory: {directory}")
            os.makedirs(directory, exist_ok=True)
            print(f"Directory created or exists: {directory}")
            with open(filename, "a") as file:
                time_str = time.strftime("%Y-%m-%d-%H:%M:%S")
                file.write(f"{time_str} {json.dumps(data)}\n")
        except Exception as e:
            print(f"Error writing to file {filename}: {e}")

    def save_data_periodically(self):
        try:
            tempture , humidity = self.sensor.getEnviroment()
            airconditioner , ontime = self.sensor.getAirConditioner()
            data = {
                "temperature": tempture,
                "humidity": humidity,
                "isPeople": self.sensor.getMotion(),
                "lux":self.sensor.getLux(),
                "useairconditionaer":airconditioner,
                "airconditionaertime":ontime
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