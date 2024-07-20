import cgsensor
from gpiozero import LED, MotionSensor
from enum import Enum
import time
import threading

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
        self.bme280 = cgsensor.BME280(i2c_addr=0x76)

    def getLux(self):
        self.setLED(setLEDColor.OFF)
        self.setLED(setLEDColor.RED)
        tsl2572 = cgsensor.TSL2572()
        if(tsl2572.single_auto_measure()):
            return float(tsl2572.illuminance)
        else:
            return -1
    
    def getMotion(self):
        return pir.value == 1
    
    def getEnviroment(self):
        if(self.bme280.forced()):
            return self.bme280.temperature ,self.bme280.humidity
    
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
