import concurrent.futures
import logging

from light import PointLight
from material import Material
from mesh import Mesh
from ray import Ray
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

        """
        for x in range(0, self.screen.width):

            print(f' {str(x / self.screen.width)}% finished.')

            for y in range(0, self.screen.height):
                # print(f' {str(x / self.screen.width)}% finished. x: {x}, y {y}')
                curr_ray: Ray = self.camera.get_cam_space_ray_at_pixel(x, y, self.screen.width, self.screen.height, 1)

                # print(f"ray for x: {x} y: {y} is ray with dir: {str(curr_ray.direction)} at origin: {str(curr_ray.origin)}")

                # check every triangle in scene
                for mesh in self.meshes:
                    for face_index, face in enumerate(mesh.faces):
                        face_normal = mesh.normals[face_index]

                        # let's try to do this in camera space to avoid ray -> world space complications

                        world_space_vertices: list = []
                        camera_space_vertices: list = []

                        for index in face:
                            w_vert = mesh.transform.apply_to_point(mesh.verts[index])
                            world_space_vertices.append(w_vert)

                            c_vert = self.camera.project_point(w_vert)
                            camera_space_vertices.append(c_vert)
                            # print(f"cs vert: {str(c_vert)}")

                        if math_helper.ray_triangle_intersection(curr_ray, camera_space_vertices[0], camera_space_vertices[1], camera_space_vertices[2],0, 100):
                            print("hit!")
                            print(f"ray for x: {x} y: {y} is ray with dir: {str(curr_ray.direction)} at origin: {str(curr_ray.origin)}")
                            image_buffer_l[x, y] = mesh.diffuse_color * 255
            """

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
        point_hit: np.array = world_space_ray.at(eye_record.t)

        # add ambient color
        color = eye_record.material.ka * np.array(ambient_light)

        # check if hit by light, if so add diffuse and specular color
        point_to_light_vec: np.array = light.transform.get_position() - point_hit
        distance_from_point_to_light: float = math_helper.magnitude(point_to_light_vec)

        shadow_ray: Ray = Ray(point_hit, point_to_light_vec)
        scene_hit_before_light, shadow_record = scene.hit(shadow_ray, EPSILON, distance_from_point_to_light)

        if not scene_hit_before_light:
            normalized_light: np.array = math_helper.get_normalized(point_to_light_vec)
            normalized_direction: np.array = math_helper.get_normalized(-world_space_ray.direction)
            h: np.array = math_helper.get_normalized(normalized_light + normalized_direction)

            diffuse_component = material.kd * material.diffuse_color * max(0, math_helper.dot(eye_record.face_normal, point_to_light_vec))
            specular_component = material.ks * material.specular_color * pow(math_helper.dot(eye_record.face_normal, h), material.p)

            print(f'ambient component: {color}')
            print(f'diffuse component: {diffuse_component}')
            print(f'specular component: {specular_component}')

            color += light.intensity * (diffuse_component + specular_component)

        return x, y, color * 255

    return x, y, None

    #     for face_index, face in enumerate(mesh.faces):
    #         face_normal = mesh.normals[face_index]
    #
    #         # let's try to do this in camera space to avoid ray -> world space complications
    #
    #         world_space_vertices: list = []
    #         camera_space_vertices: list = []
    #
    #         for index in face:
    #             w_vert = mesh.transform.apply_to_point(mesh.verts[index])
    #             world_space_vertices.append(w_vert)
    #
    #             c_vert = renderer.camera.project_point(w_vert)
    #             camera_space_vertices.append(c_vert)
    #             # print(f"cs vert: {str(c_vert)}")
    #
    #         if math_helper.ray_triangle_intersection(curr_ray, camera_space_vertices[0], camera_space_vertices[1], camera_space_vertices[2],0, 100):
    #             print("hit!")
    #             print(f"ray for x: {x} y: {y} is ray with dir: {str(curr_ray.direction)} at origin: {str(curr_ray.origin)}")
    #             # renderer.set_image_buffer(x, y, mesh.diffuse_color * 255)
    #             return x, y, mesh.diffuse_color * 255
    #
    #
    # # return x, y, None