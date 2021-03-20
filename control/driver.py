from __future__ import annotations

import time
from typing import Tuple, Callable, Optional, Union

import Adafruit_PCA9685
from RpiMotorLib import RpiMotorLib

import attributes
import sensing
import util

_MIN_ANGLE: float = -20
_MAX_ANGLE: float = 20

_STEP_UNIT: int = 80  # number of steps to do at a time
_DISTANCE_PER_STEP: float = 0.0125  # movement in mm per step TODO: check if value is correct
_MOTOR_TYPE: str = "DRV8825"


class _Pins:
    DIRECTION: int = 20
    STEP: int = 21
    MODE: Tuple[int, int, int] = (24, 25, 26)  # TODO: check if values are correct


class Direction:
    FORWARD: int = 0
    BACKWARD: int = 1


_Direction: type = Union[Direction.FORWARD, Direction.BACKWARD]
_DrivingMotor: type = RpiMotorLib.A4988Nema
_SteeringMotor: type = Adafruit_PCA9685.PCA9685


def _calculate_angle_pwm(angle: float) -> float:
    """ Converts a steering angle to a pulse width modulation (PWM) value to address the steering motor accordingly.

    Notes:
        The parameters for the PWM approximation function defined as agent attributes must be in descending exponential
        order (k0 * x^(n-1) + k1 * x^(n-2) + ... + kn).

    Args:
      angle: Angle in degrees to be converted to PWM.

    Returns:
        The PWM value for the steering angle.
    """

    # get steering parameters in reversed order -> k0, ..., kn
    coefficients = reversed(attributes.STEERING_PARAMETERS)

    # sum up polynomial approximation of the pwm value -> k0 * x^0 + ... kn * x^(n-1)
    return sum(coefficient * (angle ** exponent) for exponent, coefficient in enumerate(coefficients))


@util.SingleUse
class Driver:
    def __init__(self):
        # TODO: factor out magic numbers
        self.steering_motor: _SteeringMotor = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
        self.steering_motor.set_pwm_freq(50)
        self._driving_motor: _DrivingMotor = RpiMotorLib.A4988Nema(_Pins.DIRECTION, _Pins.STEP, _Pins.MODE, _MOTOR_TYPE)

        self._current_mode: Optional[_Mode] = None

    # TODO: add documentation
    def forward(self) -> _Mode:
        return self._mode(Direction.FORWARD)

    # TODO: add documentation
    def backward(self) -> _Mode:
        return self._mode(Direction.BACKWARD)

    # TODO: add documentation
    def _mode(self, direction: _Direction) -> _Mode:
        if self._current_mode is not None:
            self._current_mode.stop()

        self._current_mode = _Mode(self._driving_motor, direction)
        return self._current_mode

    # TODO: add documentation
    def steer(self, angle: float) -> None:
        # ensure that angle is within boundaries
        angle = max(_MIN_ANGLE, min(_MAX_ANGLE, angle))

        # calculate and set pwm value
        pwm = _calculate_angle_pwm(angle)
        self.steering_motor.set_pwm(0, 0, pwm)  # TODO: factor out magic numbers


class _Mode:
    def __init__(self, driving_motor: _DrivingMotor, direction: _Direction):
        self._active: bool = True
        self._driving_motor: _DrivingMotor = driving_motor
        self._forward: direction = self._forward == Direction.FORWARD

    # TODO: add documentation
    def do_while(self, condition: Callable[[], bool]) -> None:
        while self._active and condition():
            self._go(_STEP_UNIT)

    # TODO: add documentation
    def do_for(self, distance: float) -> None:
        steps = int(round(_STEP_UNIT * distance, 0))
        self._go(steps)

    # TODO: add documentation
    def _go(self, steps: int) -> None:
        while self._active and steps >= _STEP_UNIT:
            if self._movement_possible(_STEP_UNIT):
                self._driving_motor.motor_go(clockwise=self._forward, steps=_STEP_UNIT)
                steps -= _STEP_UNIT
            else:
                time.sleep(1)

        if self._movement_possible(steps):
            self._driving_motor.motor_go(clockwise=self._forward, steps=steps)

    # TODO: add documentation
    def _movement_possible(self, steps: int) -> bool:
        if not self._active:
            return False

        sensor = sensing.Distance.FRONT if self._forward else sensing.Distance.REAR
        predicted_distance = sensor.value - _DISTANCE_PER_STEP * steps
        return predicted_distance >= util.const.Driving.SAFETY_DISTANCE

    # TODO: add documentation
    def stop(self) -> None:
        self._active = False
