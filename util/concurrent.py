import math
import time
from collections import Callable
from typing import Any

from util.threaded import threaded


def stabilized_concurrent(name: str, min_delay: float, max_delay: float, steps: int, daemon: bool = True):
    assert min_delay < max_delay, "Minimum delay must be less than max delay."
    assert steps > 0, "It must take at least one step to reach the maximum delay."

    def calc_delay(stable_intervals: int):
        return min(max_delay, min_delay * math.exp(stable_intervals * math.log(max_delay) / steps))

    def decorator(function: Callable[[Any], bool]):
        @threaded(name, daemon)
        def concurrent_execution(*args, **kwargs):
            stable_intervals = 0

            while True:
                stable = function(*args, **kwargs)
                delay = calc_delay(stable_intervals)
                time.sleep(delay)
                stable_intervals = stable_intervals + 1 if stable else 0

        return concurrent_execution

    return decorator
