import numpy as np


class Vector3:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

        self.np_array = np.array([x, y, z])

    @staticmethod
    def from_np_array(array: np.array) -> "Vector3":
        return Vector3(array[0], array[1], array[2])
