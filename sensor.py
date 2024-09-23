import mycgsensor
from gpiozero import LED, MotionSensor
from enum import Enum
import time
import threading
import json
import os
import bisect
import os
class setLEDColor(Enum):
    OFF = [0, 0, 0]
    RED = [1, 0, 0]
    GREEN = [0, 1, 0]
    BLUE = [0, 0, 1]
    YELLOW = [1, 1, 0]
    PURPLE = [1, 0, 1]
    SKY = [0, 1, 1]
    WHITE = [1, 1, 1]

led_red = LED(18)
led_green = LED(17)
led_blue = LED(22)
pir = MotionSensor(27)

class Sensor:
    def __init__(self):
        self.bme280 = mycgsensor.BME280(i2c_addr=0x76)
        self.tsl2572 = mycgsensor.TSL2572()
        print()

    def getLux(self):
        self.setLED(setLEDColor.OFF)
        self.setLED(setLEDColor.RED)
        tsl2572 = self.tsl2572
        if(tsl2572.single_auto_measure()):
            return float(tsl2572.illuminance)
        else:
            return -1
    
    def getMotion(self):
        return pir.value == 1
    
    def getEnviroment(self) -> tuple:
        _temperature: float
        _humidity: float
        try:
            if self.bme280.forced():
                _temperature = float(self.bme280.temperature)
                _humidity = float(self.bme280.humidity)
                print(f"Temperature: {_temperature}, Humidity: {_humidity}")
                return _temperature, _humidity
            else:
                print("Forced method did not return True")
        except Exception as e:
            print(f"Exception in getEnviroment: {e}")
        return 0.0, 0.0

    
    def _setLEDInternal(self, color_value):
        if color_value[0] == 1:
            led_red.on()
        else:
            led_red.off()
        
        if color_value[1] == 1:
            led_green.on()
        else:
            led_green.off()
            
        if color_value[2] == 1:
            led_blue.on()
        else:
            led_blue.off()
    
    def setLED(self, color: setLEDColor):
        color_value = color.value
        threading.Thread(target=self._setLEDInternal, args=(color_value,)).start()

    def _setLEDBlinkInternal(self, color_value, blinkTime):
        if color_value[0] == 1:
            led_red.on()
        else:
            led_red.off()
        
        if color_value[1] == 1:
            led_green.on()
        else:
            led_green.off()
            
        if color_value[2] == 1:
            led_blue.on()
        else:
            led_blue.off()
        
        if blinkTime > 0:
            time.sleep(blinkTime)
            led_red.off()
            led_green.off()
            led_blue.off()

    def setBlinkLED(self, color: setLEDColor, blinkTime=0):
        color_value = color.value
        threading.Thread(target=self._setLEDBlinkInternal, args=(color_value, blinkTime)).start()

    def getAirConditioner(self):
        current_time = time.time()

        # 30分前のタイムスタンプを計算
        time_30_min_ago = current_time - 1800  # 1800秒 = 30分
        current_path = os.getcwd()
        # 日付部分を抽出してファイル名を生成
        date_str = time.strftime("%Y-%m-%d", time.localtime(current_time))
        filename = f"{current_path}/datalog/{date_str}_data_log.txt"
        directory = f"{current_path}/datalog/"

        # ファイルが存在しない場合、最新のファイルを探す
        if not os.path.exists(filename):
            files = os.listdir(directory)
            full_paths = [os.path.join(directory, f) for f in files if os.path.isfile(os.path.join(directory, f))]
            
            if not full_paths:
                raise FileNotFoundError(f"{directory} 内にファイルが見つかりません。")

            # 最終更新日時が最新のファイルを探す
            latest_file = max(full_paths, key=os.path.getmtime)
            filename = latest_file
            print(f"指定されたファイルが見つからなかったため、最新のファイル {filename} を使用します。")

        with open(filename, "r") as file:
            lines = file.readlines()

        # ファイルが空の場合の対処
        if not lines:
            print(f"ファイル {filename} にデータがありません。デフォルト値を返します。")
            # デフォルト値として False と現在時刻を返す
            return False, time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(current_time))

        timestamps = []
        data = []
        for line in lines:
            try:
                log_time_str, log_data = line.split(" ", 1)
                log_time = time.strptime(log_time_str, "%Y-%m-%d-%H:%M:%S")
                log_timestamp = time.mktime(log_time)
                timestamps.append(log_timestamp)
                data.append(log_data)
            except Exception as e:
                print(f"ログデータの解析中にエラーが発生しました: {e}")
                continue  # エラーがあっても他の行を処理し続ける

        # データが空でないか確認
        if not data:
            print("有効なデータがありません。デフォルト値を返します。")
            return False, time.strftime("%Y-%m-%d-%H-%M-%S", pos_30_min_ago)

        # 最新のデータを取得
        latest_data = json.loads(data[-1])  # 最後のデータが最新
        latest_temp = latest_data["temperature"]

        # 30分前のデータの位置を探す
        pos_30_min_ago = bisect.bisect_left(timestamps, time_30_min_ago)

        if pos_30_min_ago < len(timestamps):
            closest_30_min_ago_data = json.loads(data[pos_30_min_ago])
            temp_30_min_ago = closest_30_min_ago_data["temperature"]
        else:
            temp_30_min_ago = latest_temp  # 30分前のデータがない場合、温度差を0にする

        temp_difference = latest_temp - temp_30_min_ago

        air_conditioner = temp_difference >= 1

        if not air_conditioner:
            pos_30_min_ago = 0

        # 30分前の時間をYYYY-MM-DD-hh-mm-ssで返す
        time_30_min_ago_str = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time_30_min_ago))

        return air_conditioner, time_30_min_ago_str

