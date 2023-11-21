import numpy as np

from ray import Ray
from vector import Vector3

def dot(v1: np.array, v2: np.array) -> np.array:
    return np.dot(v1, v2)


def cross(v1: np.array, v2: np.array) -> np.array:
    if v1.shape != (3,) or v2.shape != (3,):
        raise Exception("np.array vectors not of correct shape to do cross product")

    return np.cross(v1, v2)


def magnitude(v1: np.array) -> float:
    return np.sqrt(np.sum(np.power(v1, 2)))


def check_if_vectors_identical(v1: np.array, v2: np.array) -> bool:
    return np.array_equal(v1, v2)


def multiply_matrices(v1: np.array, v2: np.array) -> np.array:
    if v1.shape[1] != v2.shape[0]:
        raise Exception("Malformed matrix multiplication")

    return np.matmul(v1, v2)


def get_normalized(v1: np.array) -> np.array:
    return v1 / magnitude(v1)


def get_3d_barycentric_coords(p: np.array, a: np.array, b: np.array, c: np.array) -> np.array:
    """
    - p is the 3d point being tested against the triangle
    - a, b and c are the triangle's 3d vertices
    - returned is the values of [alpha, beta, gamma] (as in the book)
    """

    triangle_normal = cross(b - a, c - a)

    triangle_area: float = dot(triangle_normal, triangle_normal)  # pow(magnitude(n), 2)

    n_a: np.array = cross((c - b), (p - b))
    alpha: np.array = dot(triangle_normal, n_a) / triangle_area

    n_b: np.array = cross((a - c), (p - c))
    beta: np.array = dot(triangle_normal, n_b) / triangle_area

    n_c: np.array = cross((b - a), (p - a))
    gamma: np.array = dot(triangle_normal, n_c) / triangle_area

    return np.array([alpha, beta, gamma])


def get_2d_barycentric_coords(p: np.array, a: np.array, b: np.array, c: np.array) -> np.array:
    """
    - p is the point being tested against the triangle
    - a, b and c are the triangle's vertices
    - returned is the values of [alpha, beta, gamma] (as in the book)
    """

    x_a: float = a[0]
    y_a: float = a[1]

    x_b: float = b[0]
    y_b: float = b[1]

    x_c: float = c[0]
    y_c: float = c[1]

    x: float = p[0]
    y: float = p[1]

    # print(x_a, y_a, x_b, y_b, x_c, y_c, x, y)

    gamma_numer: float = ((y_a - y_b) * x) + ((x_b - x_a) * y) + ((x_a * y_b) - (x_b * y_a))
    gamma_denom: float = ((y_a - y_b) * x_c) + ((x_b - x_a) * y_c) + ((x_a * y_b) - (x_b * y_a))

    if gamma_denom == 0:
        gamma = 0
    else:
        gamma: float = gamma_numer / gamma_denom

    beta_numer: float = ((y_a - y_c) * x) + ((x_c - x_a) * y) + ((x_a * y_c) - (x_c * y_a))
    beta_denom: float = ((y_a - y_c) * x_b) + ((x_c - x_a) * y_b) + ((x_a * y_c) - (x_c * y_a))

    if beta_denom == 0:
        beta = 0
    else:
        beta: float = beta_numer / beta_denom

    alpha: float = 1 - beta - gamma

    return np.array([alpha, beta, gamma])


def ray_triangle_intersection(ray: Ray, a_point: Vector3, b_point: Vector3, c_point: Vector3, t0: float, t1: float) -> bool:

    EPSILON = 0.00001

    a = a_point.x - b_point.x  # c
    b = a_point.y - b_point.y  # c
    c = a_point.z - b_point.z  # c
    d = a_point.x - c_point.x  # c
    e = a_point.y - c_point.y  # c
    f = a_point.z - c_point.z  # c
    g = ray.direction.x  # c
    h = ray.direction.y  # c
    i = ray.direction.z  # c
    j = a_point.x - ray.origin.x  # c
    k = a_point.y - ray.origin.y  # c
    l = a_point.z - ray.origin.z  # c

    ei_minus_hf = e*i - h*f
    gf_minus_di = g*f - d*i
    dh_minus_eg = d*h - e*g

    M = a*ei_minus_hf + b*gf_minus_di + c*dh_minus_eg

    if abs(M) < EPSILON:
        return False

    ak_minus_jb = a*k - j*b
    jc_minus_al = j*c - a*l
    bl_minus_kc = b*l - k*c

    t = -(f*ak_minus_jb + e*jc_minus_al + d*bl_minus_kc) / M

    if t < t0 or t > t1:
        return False

    theta = (i*ak_minus_jb + h*jc_minus_al + g*bl_minus_kc) / M

    if theta < 0 or theta > 1:
        return False

    beta = (j*ei_minus_hf + k*gf_minus_di + l*dh_minus_eg) / M

    if beta < 0 or beta > (1 - theta):
        return False

    return True
