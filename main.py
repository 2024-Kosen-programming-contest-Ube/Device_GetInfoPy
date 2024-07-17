from data_log import DataLogger
import http_server
from Config import Config
def main():
    config = Config('config.txt')
    logger = DataLogger("./datalog/data_log.txt", config.save_interval, config.send_interval)
    logger.start_periodic_saving()

    http_server.run_server()

if __name__ == "__main__":
    main()
