import numpy as np
import math_helper
import math


class Transform:

    def __init__(self):
        self.matrix: np.array = np.identity(4)

    def transformation_matrix(self) -> np.array:
        return self.matrix

    def set_position(self, x, y, z) -> None:
        self.matrix[0][3] = x
        self.matrix[1][3] = y
        self.matrix[2][3] = z

    # def get_position(self) -> np.array:
    #     x = self.matrix[0][3]
    #     y = self.matrix[1][3]
    #     z = self.matrix[2][3]
    #     return np.array([x, y, z])

    def set_rotation(self, x, y, z) -> None:
        # XYZ ordered rotation
        x_rad = math.radians(x)
        y_rad = math.radians(y)
        z_rad = math.radians(z)

        c_z: float = math.cos(z_rad)
        s_z: float = math.sin(z_rad)
        z_mat: np.array = np.array([
            [c_z,   -s_z,     0],
            [s_z,   c_z,   0],
            [0,     0,      1],
        ])

        c_y: float = math.cos(y_rad)
        s_y: float = math.sin(y_rad)
        y_mat: np.array = np.array([
            [c_y,   0,    s_y],
            [0,     1,    0],
            [-s_y,   0,    c_y],
        ])

        c_x: float = math.cos(x_rad)
        s_x: float = math.sin(x_rad)
        x_mat: np.array = np.array([
            [1,     0,      0],
            [0,     c_x,    -s_x],
            [0,     s_x,    c_x],
        ])

        yx = math_helper.multiply_matrices(x_mat, y_mat)
        self.matrix[0:3, 0:3] = math_helper.multiply_matrices(yx, z_mat)

    def inverse_matrix(self) -> np.array:
        inverse = np.identity(4)

        # transpose of inverse is sufficient for our purpose
        inverse[0:3, 0:3] = self.matrix[0:3, 0:3].T

        # 3x3 mult 3x1 -> 3x1
        inverse[0:3, 3] = math_helper.multiply_matrices(inverse[0:3, 0:3] * -1, self.matrix[0:3, 3])

        return inverse

    def apply_to_point(self, p) -> np.array:
        a_p: np.array = np.append(p, 1)
        return math_helper.multiply_matrices(self.matrix, a_p)[0:3]
    
    def apply_inverse_to_point(self, p) -> np.array:
        a_p: np.array = np.append(p, 1)
        # 4x4 times 4x1 -> 4x1 -> 3x1
        return math_helper.multiply_matrices(self.inverse_matrix(), a_p)[0:3]
    
    def apply_to_normal(self, n) -> np.array:
        a_n: np.array = np.append(n, 0)
        return math_helper.multiply_matrices(self.matrix, a_n)[0:3]

    # EXTRA CREDIT
    def set_axis_rotation(self, axis, rotation) -> None:
        rot_in_radians: float = math.radians(rotation)
        k: np.array = math_helper.get_normalized(axis)
        k_mat = np.array([
            [0,     -k[2],  k[1]],
            [k[2],  0,      -k[0]],
            [-k[1], k[0],   0]
        ])

        e0: np.array = np.identity(3)
        e1: np.array = math.sin(rot_in_radians) * k_mat
        e2: np.array = (1 - math.cos(rot_in_radians)) * math_helper.multiply_matrices(k_mat, k_mat)

        result = e0 + e1 + e2

        self.matrix[0:3, 0:3] = result
