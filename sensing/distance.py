from datetime import datetime

from gpiozero import DistanceSensor

UPDATE_INTERVAL = 0.4


class TriggerPins:
    FRONT = 18
    RIGHT = 23
    BACK = 25
    BACK_ANGLED = 24


class EchoPins:
    FRONT = 4
    RIGHT = 17
    BACK = 22
    BACK_ANGLED = 27


class UltrasonicSensor:
    @property
    def value(self) -> float:
        passed_time = datetime.now() - self._last_update
        if passed_time.seconds >= UPDATE_INTERVAL:
            self._last_update = datetime.now()
            self._value = self._sensor.distance * 100

        return self._value

    def __init__(self, echo_pin: int, trigger_pin: int):
        self._sensor: DistanceSensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin)
        self._value: float = 0.0
        self._last_update: datetime = datetime.now()


UltrasonicSensor.FRONT = UltrasonicSensor(EchoPins.FRONT, TriggerPins.FRONT)
UltrasonicSensor.RIGHT = UltrasonicSensor(EchoPins.RIGHT, TriggerPins.RIGHT)
UltrasonicSensor.REAR = UltrasonicSensor(EchoPins.BACK, TriggerPins.BACK)
UltrasonicSensor.REAR_ANGLED = UltrasonicSensor(EchoPins.BACK_ANGLED, TriggerPins.BACK_ANGLED)
