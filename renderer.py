import concurrent.futures
import datetime
import logging
import threading

from light import PointLight
from material import Material
from mesh import Mesh
from ray import Ray
from ray_triangle_intersection_result import RayTriangleIntersectionResult
from scene import Scene
from screen import Screen
from camera import PerspectiveCamera, OrthoCamera

import numpy as np
import math_helper

EPSILON = 0.00001

class Renderer:

    def __init__(self, screen: Screen, camera, meshes: list[Mesh], light_):
        self.screen = screen
        self.camera = camera
        self.meshes = meshes
        self.scene = Scene(meshes)

        self.light = light_

        self.image_buffer: np.array = np.zeros(1)

        self.increment_pixel_lock = threading.Lock()
        self.pixels_completed: float = 0.0

    def set_image_buffer(self, x, y, color):
        self.image_buffer[x, y] = color

    def increment_pixels_finished(self):
        with self.increment_pixel_lock:
            self.pixels_completed += 1.0
            if self.pixels_completed % 500 == 0:
                total_pixels = self.screen.width * self.screen.height
                print(str(100.0 * (self.pixels_completed / total_pixels)) + "% complete")

    def render(self, shading, bg_color: list, ambient_light) -> None:

        render_start_time = datetime.datetime.now()

        image_buffer_l: np.array = np.full((self.screen.width, self.screen.height, 3), bg_color)
        # self.image_buffer: np.array = np.full((self.screen.width, self.screen.height, 3), bg_color)

        args_list = list()

        for x in range(0, self.screen.width):
            for y in range(0, self.screen.height):
                args_list.append((x, y, ambient_light, self))

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)
        results = executor.map(thread_function, args_list)

        for value in results:
            # print(value)
            x = value[0]
            y = value[1]
            color = value[2]

            if color is not None:
                if color.shape != (3,):
                    print("shape not (3,) " + str(color))

                image_buffer_l[x, y] = color

        print("drawing buffer")
        self.screen.draw(image_buffer_l)

        self.screen.do_capture()

        render_end_time = datetime.datetime.now()

        render_duration: datetime.timedelta = render_end_time - render_start_time
        total_seconds = render_duration.total_seconds()
        minutes, seconds = divmod(total_seconds, 60)

        print(f'Rendering took {minutes}m and {seconds}s')


    def ray_color(self, ray_w: Ray, ambient_light: np.array, recursion_depth: int, max_recursion_depth: int) -> np.array:

        if recursion_depth == max_recursion_depth:
            return np.array([0, 0, 0])

        light: PointLight = self.light
        scene: Scene = self.scene

        scene_hit_from_eye, eye_record = scene.hit(ray_w, 0, 100)

        if not scene_hit_from_eye:
            #if recursion_depth == 0:
            return np.array([99 / 255.0, 215 / 255.0, 228 / 255.0])
            #else:
            #    return np.array([0, 0, 0])

        normal_w: np.array = eye_record.normal_w

        material: Material = eye_record.material
        point_hit: np.array = eye_record.point_hit

        # add ambient color
        color = eye_record.material.ka * np.array(ambient_light)

        # check if hit by light, if so add diffuse and specular color
        light_position: np.array = light.transform.apply_to_point(np.array([0, 0, 0]))
        point_to_light_vec: np.array = light_position - point_hit
        point_to_light_vec_normalized: np.array = math_helper.get_normalized(point_to_light_vec)
        distance_from_point_to_light: float = math_helper.magnitude(point_to_light_vec)

        # print(f'point_hit {str(point_hit)}, light position {str(light_position)}, point_to_light_vec {str(point_to_light_vec)}')

        shadow_ray: Ray = Ray(point_hit, point_to_light_vec)
        scene_hit_before_light, shadow_record = scene.hit(shadow_ray, EPSILON, 1000)

        # return just ambient light if we're in shadow
        if scene_hit_before_light:
            return color

        # print(f'face_normal: {eye_record.face_normal}, point_to_light_vec: {point_to_light_vec}, fn dot ptlv: {math_helper.dot(eye_record.face_normal, point_to_light_vec)}')
        # print(f'point_hit: {point_hit} face_normal: {eye_record.face_normal}, point_to_light_vec: {point_to_light_vec} normalized_neg_dir: {normalized_neg_direction} h: {h}, fn dot h: {math_helper.dot(eye_record.face_normal, h)}')

        d_sq = pow(distance_from_point_to_light, 2)
        cos_t = max(0, math_helper.dot(point_to_light_vec_normalized, normal_w))

        e = light.intensity * light.color * (1 / d_sq) * cos_t

        diffuse_coefficient = material.kd
        diffuse_ray_color = diffuse_coefficient * material.diffuse_color / np.pi

        specular_coefficient = material.ks
        normalized_neg_direction: np.array = math_helper.get_normalized(-ray_w.direction)
        h: np.array = math_helper.get_normalized(point_to_light_vec_normalized + normalized_neg_direction)
        spec_calc = pow(max(0, math_helper.dot(h, normal_w)), material.p)

        specular_ray_color = specular_coefficient * material.specular_color * spec_calc

        color += e * (specular_ray_color + diffuse_ray_color)

        reflection_coefficient = material.km
        if reflection_coefficient > 0:
            reflection_direction: np.array = ray_w.direction - 2 * math_helper.dot(ray_w.direction, normal_w) * normal_w
            reflection_ray: Ray = Ray(point_hit, reflection_direction)
            color += reflection_coefficient * self.ray_color(reflection_ray, ambient_light, recursion_depth + 1, max_recursion_depth)

        return np.clip(color, 0, 1)


def thread_function(args: any) -> any:

    x = args[0]
    y = args[1]
    ambient_light = args[2]
    renderer = args[3]

    curr_ray: Ray = renderer.camera.get_cam_space_ray_at_pixel(x, y, renderer.screen.width, renderer.screen.height, 1)
    world_space_ray: Ray = renderer.camera.inverse_project_ray(curr_ray)

    # print(f'dir curr_ray {str(curr_ray.direction)}, world_space_ray {str(world_space_ray.direction)}')
    # print(f'origin curr_ray {str(curr_ray.origin)}, world_space_ray {str(world_space_ray.origin)}')

    color: np.array = renderer.ray_color(world_space_ray, ambient_light, 0, 3)

    renderer.increment_pixels_finished()

    return x, y, np.clip(color, 0, 1) * 255
