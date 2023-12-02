import numpy as np
from material import Material
from ray_triangle_intersection_result import RayTriangleIntersectionResult


class HitRecord:

    def __init__(self, point_hit: np.array, face_normal: np.array, intersection_result: RayTriangleIntersectionResult, w_normal: np.array, material: Material):
        self.point_hit: np.array = point_hit
        self.face_normal: np.array = face_normal
        self.intersection_result: np.array = intersection_result
        self.normal_w = w_normal
        self.material = material
