import numpy as np


class Vector3:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

        self.np_array = np.array([x, y, z], float)

    def __str__(self):
        return str(self.np_array)

    @staticmethod
    def from_np_array(array: np.array) -> "Vector3":
        return Vector3(array[0], array[1], array[2])
