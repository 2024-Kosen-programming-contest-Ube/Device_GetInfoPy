from data_log import DataLogger
import http_server
from Config import Config
from sensor import Sensor,setLEDColor
import os
def main():
    sensor=Sensor()
    current_path = os.getcwd()
    config = Config(f'{current_path}/config.txt')
    logger = DataLogger(f'{current_path}/datalog/data_log.txt', config.save_interval, config.send_interval)
    logger.start_periodic_saving()
    http_server.run_server()
    

if __name__ == "__main__":
    main()
