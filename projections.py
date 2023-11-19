import numpy as np

import math_helper


class OrthographicProjection:

    def __init__(self, left, right, bottom, top, near, far):
        self.projection: np.array = np.identity(4)
        self.inverse_projection: np.array = np.identity(4)

        self.projection[0, 0] = 2 / (right - left)
        self.projection[1, 1] = 2 / (far - near)
        self.projection[2, 2] = 2 / (top - bottom)

        self.projection[0, 3] = -((right + left) / (right - left))
        self.projection[1, 3] = -((far + near) / (far - near))
        self.projection[2, 3] = -((top + bottom) / (top - bottom))

        self.inverse_projection[0, 0] = (right - left) / 2
        self.inverse_projection[1, 1] = (far - near) / 2
        self.inverse_projection[2, 2] = (top - bottom) / 2

        self.inverse_projection[0, 3] = (right + left) / 2
        self.inverse_projection[1, 3] = (far + near) / 2
        self.inverse_projection[2, 3] = (top + bottom) / 2

        # ADDED TO DEBUG
        self.inverse_projection = np.linalg.inv(self.projection)

    def apply_to_point(self, p) -> np.array:
        a_p: np.array = np.append(p, 1).transpose()
        return math_helper.multiply_matrices(self.projection, a_p)[0:3]

    def apply_inverse_to_point(self, p) -> np.array:
        a_p: np.array = np.append(p, 1).transpose()
        return math_helper.multiply_matrices(self.inverse_projection, a_p)[0:3]


class PerspectiveProjection:
    def __init__(self, near, far):
        self.near = near
        self.far = far

        self.projection: np.array = np.array([
            [near, 0, 0, 0],
            [0, far + near, 0, -far * near],
            [0, 0, near, 0],
            [0, 1, 0, 0]
        ])

        self.inverse_projection: np.array = np.array([
            [1 / near, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1 / near, 0],
            [0, 1 / (far * near), 0, ((near + far) / (far * near))]
        ])

    def apply_to_point(self, p: np.array) -> np.array:
        a_p: np.array = np.append(p, 1)
        point_in_camera_space: np.array = math_helper.multiply_matrices(self.projection, a_p)
        point_in_camera_space /= point_in_camera_space[3]

        return point_in_camera_space[0:3]

    def apply_inverse_to_point(self, p: np.array) -> np.array:
        a_p: np.array = np.append(p, 1)
        y_c = (self.far * self.near) / (self.near + self.far - a_p[1])
        a_p *= y_c
        return math_helper.multiply_matrices(self.inverse_projection, a_p)[0:3]
