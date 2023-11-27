import numpy as np


class HitRecord:

    def __init__(self, point_hit: np.array, face_normal: np.array, t: float):
        self.point_hit: np.array = point_hit
        self.face_normal: np.array = face_normal
        self.t: np.array = t
