import math

import numpy as np

import math_helper
from projections import OrthographicProjection, PerspectiveProjection
from ray import Ray
from transform import Transform


class OrthoCamera:

    def __init__(self, left, right, bottom, top, near, far):
        self.transform = Transform()
        self.orthographic_projection = OrthographicProjection(left, right, bottom, top, near, far)

        self._ratio = abs(right - left) / abs(top - bottom)

        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.near = near
        self.far = far

    def ratio(self) -> float:
        return self._ratio

    def project_point(self, p) -> np.array:
        return self.transform.apply_inverse_to_point(p)
        # return self.orthographic_projection.apply_to_point(p)

    def inverse_project_point(self, p) -> np.array:
        # p = self.orthographic_projection.apply_inverse_to_point(p)
        return self.transform.apply_to_point(p)
        # return p

    def project_ray(self, ray: Ray) -> Ray:
        origin = self.project_point(ray.origin)
        direction = self.project_point(ray.direction)

        return Ray(origin, direction)

    def inverse_project_ray(self, ray: Ray) -> Ray:
        direction = self.inverse_project_point(ray.direction)
        origin = self.inverse_project_point(ray.origin)

        return Ray(origin, direction)

    def get_cam_space_ray_at_pixel(self, pixel_i: int, pixel_j: int, pixel_width: int, pixel_height: int, focal_distance: int) -> Ray:
        u = self.left + (self.right - self.left) * (pixel_i + 0.5) / pixel_width
        v = self.bottom + (self.top - self.bottom) * (pixel_j + 0.5) / pixel_height

        u_u: np.array = np.array([1, 0, 0]) * u
        v_v: np.array = np.array([0, 0, 1]) * v
        origin: np.array = u_u + v_v

        direction: np.array = np.array([0, 1, 0])

        return Ray(origin, direction)


class PerspectiveCamera:
    def __init__(self, left, right, bottom, top, near, far):
        self.transform = Transform()
        self.orthographic_projection = OrthographicProjection(left, right, bottom, top, near, far)
        self.perspective_projection = PerspectiveProjection(near, far)

        self._ratio = abs(right - left) / abs(top - bottom)

        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.near = near
        self.far = far

    def ratio(self) -> float:
        return self._ratio

    def project_point(self, p) -> np.array:
        p = self.transform.apply_inverse_to_point(p)
        p = self.perspective_projection.apply_to_point(p)
        p = self.orthographic_projection.apply_to_point(p)
        return p[0:3]

    def inverse_project_point(self, p) -> np.array:
        p = self.orthographic_projection.apply_inverse_to_point(p)
        p = self.perspective_projection.apply_inverse_to_point(p)
        p = self.transform.apply_to_point(p)
        return p

    def project_ray(self, ray: Ray) -> Ray:
        direction = self.project_point(ray.direction)
        origin = self.project_point(ray.origin)

        return Ray(origin, direction)

    def inverse_project_ray(self, ray: Ray) -> Ray:
        direction = self.inverse_project_point(ray.direction)
        origin = self.inverse_project_point(ray.origin)

        return Ray(origin, direction)

    def get_cam_space_ray_at_pixel(self, pixel_i: int, pixel_j: int, pixel_width: int, pixel_height: int, focal_distance: int) -> Ray:
        u = self.left + (self.right - self.left) * (pixel_i + 0.5) / pixel_width
        v = self.bottom + (self.top - self.bottom) * (pixel_j + 0.5) / pixel_height

        u_u: np.array = np.array([1, 0, 0]) * u
        v_v: np.array = np.array([0, 0, 1]) * v
        d_w: np.array = np.array([0, 1, 0]) * focal_distance
        direction: np.array = u_u + v_v + d_w
        direction = math_helper.get_normalized(direction)

        origin: np.array = np.array([0, 0, 0])

        return Ray(origin, direction)

    @staticmethod
    def from_FOV(fov, near, far, ratio):
        right: float = math.tan(math.radians(fov) / 2) * abs(near)
        left: float = -right

        top: float = right / ratio
        bottom: float = -top

        return PerspectiveCamera(left, right, bottom, top, near, far)
