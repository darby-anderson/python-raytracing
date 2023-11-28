import numpy as np
from material import Material


class HitRecord:

    def __init__(self, point_hit: np.array, face_normal: np.array, t: float, material: Material):
        self.point_hit: np.array = point_hit
        self.face_normal: np.array = face_normal
        self.t: np.array = t
        self.material = material
