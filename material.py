import numpy as np


class Material:

    def __init__(self, ka: float, kd: float, diffuse_color: np.array, ks: float, specular_color: np.array, p: float):
        self.ka: float = ka
        self.kd: float = kd
        self.ks: float = ks
        self.p: float = p

        self.diffuse_color = diffuse_color
        self.specular_color = specular_color
