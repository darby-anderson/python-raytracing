from transform import Transform
import numpy as np


class PointLight:

    def __init__(self, intensity: float, color: np.array):
        self.transform = Transform()
        self.intensity = intensity
        self.color = color
