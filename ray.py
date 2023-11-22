import numpy as np
import math_helper


class Ray:

    def __init__(self, origin: np.array, direction: np.array):
        self.origin: np.array = origin
        self.direction: np.array = direction

    def normalize(self):
        self.direction = math_helper.get_normalized(self.direction)
