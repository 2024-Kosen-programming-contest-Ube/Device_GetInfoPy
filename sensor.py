import cgsensor
from gpiozero import LED, MotionSensor

class Sensor():
    tsl2572 = cgsensor.TSL2572()
    pir = MotionSensor(27)
    
    def getLux(self):
        self.tsl2572.single_auto_measure()
        return float(self.tsl2572.illuminance)
        pass
    
    def getMotion(self):
        if self.pir.value==1:
            return True
        else:
            return False
        pass