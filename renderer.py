import concurrent.futures
import logging

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


class Renderer:

    def __init__(self, screen: Screen, camera, meshes: list[Mesh], light_):
        self.screen = screen
        self.camera = camera
        self.meshes = meshes
        self.scene = Scene(meshes)

        self.light = light_

        self.image_buffer: np.array = np.zeros(1)

    def set_image_buffer(self, x, y, color):
        self.image_buffer[x, y] = color

    def render(self, shading, bg_color: list, ambient_light) -> None:

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


def thread_function(args: any) -> any:

    EPSILON = 0.00001

    x = args[0]
    y = args[1]
    ambient_light = args[2]
    renderer = args[3]

    light: PointLight = renderer.light
    scene: Scene = renderer.scene

    curr_ray: Ray = renderer.camera.get_cam_space_ray_at_pixel(x, y, renderer.screen.width, renderer.screen.height, 1)
    world_space_ray: Ray = renderer.camera.project_ray(curr_ray)

    scene_hit_from_eye, eye_record = scene.hit(world_space_ray, 0, 100)

    if scene_hit_from_eye:

        material: Material = eye_record.material
        point_hit: np.array = eye_record.point_hit
        intersection_result: RayTriangleIntersectionResult = eye_record.intersection_result

        # add ambient color
        color = eye_record.material.ka * np.array(ambient_light)
        # color = eye_record.normal_w
        # print(f'color: {color}')

        # check if hit by light, if so add diffuse and specular color
        light_position: np.array = light.transform.apply_to_point(np.array([0, 0, 0]))
        # point_to_light_vec: np.array = math_helper.get_normalized(light_direction)
        point_to_light_vec: np.array = light_position - point_hit
        point_to_light_vec_normalized: np.array = math_helper.get_normalized(point_to_light_vec)
        # point_to_light_vec: np.array = math_helper.get_normalized(light_position)
        distance_from_point_to_light: float = math_helper.magnitude(point_to_light_vec)

        # print(f'point_hit {str(point_hit)}, light position {str(light_position)}, point_to_light_vec {str(point_to_light_vec)}')

        shadow_ray: Ray = Ray(point_hit, point_to_light_vec)
        scene_hit_before_light, shadow_record = scene.hit(shadow_ray, EPSILON, 1000)

        if not scene_hit_before_light:
            # normalized_light: np.array = math_helper.get_normalized(point_to_light_vec)


            # print(f'face_normal: {eye_record.face_normal}, point_to_light_vec: {point_to_light_vec}, fn dot ptlv: {math_helper.dot(eye_record.face_normal, point_to_light_vec)}')
            # print(f'point_hit: {point_hit} face_normal: {eye_record.face_normal}, point_to_light_vec: {point_to_light_vec} normalized_neg_dir: {normalized_neg_direction} h: {h}, fn dot h: {math_helper.dot(eye_record.face_normal, h)}')

            d_sq = pow(distance_from_point_to_light, 2)
            cos_t = max(0, math_helper.dot(point_to_light_vec_normalized, eye_record.face_normal))

            e = light.intensity * light.color * (1 / d_sq) * cos_t

            diffuse_coefficient = material.kd
            diffuse_ray_color = diffuse_coefficient * material.diffuse_color / np.pi

            # diffuse_component = material.kd * material.diffuse_color * max(0, math_helper.dot(eye_record.face_normal, point_to_light_vec))
            # specular_component = material.ks * material.specular_color * pow(max(0, math_helper.dot(eye_record.face_normal, h)), material.p)

            specular_coefficient = material.ks
            normalized_neg_direction: np.array = math_helper.get_normalized(-world_space_ray.direction)
            h: np.array = math_helper.get_normalized(point_to_light_vec_normalized + normalized_neg_direction)
            spec_calc = pow(max(0, math_helper.dot(h, eye_record.face_normal)), material.p)

            specular_ray_color = specular_coefficient * material.specular_color * spec_calc

            # print(f'ambient component: {color}')
            # print(f'diffuse component: {diffuse_component}')
            # print(f'specular component: {specular_component}')

            color += e * (specular_ray_color + diffuse_ray_color)
            # color += light.intensity * (diffuse_component)

        return x, y, np.clip(color, 0, 1) * 255

    return x, y, None
