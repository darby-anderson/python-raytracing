import numpy as np
from vector import Vector3
import math_helper

class Ray:

    def __init__(self, origin: np.array, direction: np.array):
        self.origin: Vector3 = Vector3(origin[0], origin[1], origin[2])
        self.direction: Vector3 = Vector3(direction[0], direction[1], direction[2])

    def normalize(self):
        normalized_dir = math_helper.get_normalized(self.direction.np_array)
        self.direction = Vector3(normalized_dir[0], normalized_dir[1], normalized_dir[2])
