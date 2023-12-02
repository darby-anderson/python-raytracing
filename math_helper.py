import numpy as np

from ray import Ray
from ray_triangle_intersection_result import RayTriangleIntersectionResult


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


def ray_triangle_intersection(ray: Ray, a_point: np.array, b_point: np.array, c_point: np.array, t0: float, t1: float) -> RayTriangleIntersectionResult:

    EPSILON = 0.00001

    a_point_x = a_point[0]
    a_point_y = a_point[1]
    a_point_z = a_point[2]

    b_point_x = b_point[0]
    b_point_y = b_point[1]
    b_point_z = b_point[2]

    c_point_x = c_point[0]
    c_point_y = c_point[1]
    c_point_z = c_point[2]

    ray_origin_x = ray.origin[0]
    ray_origin_y = ray.origin[1]
    ray_origin_z = ray.origin[2]

    ray_direction_x = ray.direction[0]
    ray_direction_y = ray.direction[1]
    ray_direction_z = ray.direction[2]

    a = a_point_x - b_point_x  # c
    b = a_point_y - b_point_y  # c
    c = a_point_z - b_point_z  # c
    d = a_point_x - c_point_x  # c
    e = a_point_y - c_point_y  # c
    f = a_point_z - c_point_z  # c
    g = ray_direction_x  # c
    h = ray_direction_y  # c
    i = ray_direction_z  # c
    j = a_point_x - ray_origin_x  # c
    k = a_point_y - ray_origin_y  # c
    l = a_point_z - ray_origin_z  # c

    ei_minus_hf = e*i - h*f
    gf_minus_di = g*f - d*i
    dh_minus_eg = d*h - e*g

    M = a*ei_minus_hf + b*gf_minus_di + c*dh_minus_eg

    if abs(M) < EPSILON:
        return RayTriangleIntersectionResult(False, 0, 0, 0)

    ak_minus_jb = a*k - j*b
    jc_minus_al = j*c - a*l
    bl_minus_kc = b*l - k*c

    t = -(f*ak_minus_jb + e*jc_minus_al + d*bl_minus_kc) / M

    if t < t0 or t > t1:
        return RayTriangleIntersectionResult(False, 0, 0, 0)

    theta = (i*ak_minus_jb + h*jc_minus_al + g*bl_minus_kc) / M

    if theta < 0 or theta > 1:
        return RayTriangleIntersectionResult(False, 0, 0, 0)

    beta = (j*ei_minus_hf + k*gf_minus_di + l*dh_minus_eg) / M

    if beta < 0 or beta > (1 - theta):
        return RayTriangleIntersectionResult(False, 0, 0, 0)

    return RayTriangleIntersectionResult(True, t, theta, beta)


def ray_aabb_intersection(ray: Ray, min_aabb_point: np.array, max_aabb_point: np.array) -> bool:

    ray_t_max = 1000
    ray_t_min = -1000

    for i in range(3):
        if ray.direction[i] == 0:
            inv_d = 100000
        else:
            inv_d = 1 / ray.direction[i]

        origin = ray.origin[i]

        t0 = (min_aabb_point[i] - origin) * inv_d
        t1 = (max_aabb_point[i] - origin) * inv_d

        if inv_d < 0:
            t0, t1 = t1, t0

        if t0 > ray_t_min:
            ray_t_min = t0

        if t1 < ray_t_max:
            ray_t_max = t1

        # print(f'inv_d: {inv_d} t0: {t0} t1: {t1} ray_t_min: {ray_t_min} ray_t_max: {ray_t_max}')

        if ray_t_max < ray_t_min:
            return False

    return True
