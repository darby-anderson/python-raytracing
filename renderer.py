import concurrent.futures
import logging

import light
from mesh import Mesh
from ray import Ray
from screen import Screen
from camera import PerspectiveCamera, OrthoCamera

import numpy as np
import math_helper


class Renderer:

    def __init__(self, screen: Screen, camera, meshes: list[Mesh], light_):
        self.screen = screen
        self.camera = camera
        self.meshes = meshes
        self.light = light_

        self.image_buffer: np.array = np.zeros(1)

    def set_image_buffer(self, x, y, color):
        self.image_buffer[x, y] = color

    def render(self, shading, bg_color: list, ambient_light) -> None:

        image_buffer_l: np.array = np.full((self.screen.width, self.screen.height, 3), bg_color)

        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:

            args_list = list()

            for x in range(0, self.screen.width):
                for y in range(0, self.screen.height):
                    args_list.append({x, y, self})

            executor.map(thread_function, args_list)
            executor.shutdown(wait=True)
        """

        for x in range(0, self.screen.width):

            print(f' {str(x / self.screen.width)}% finished.')

            for y in range(0, self.screen.height):
                # print(f' {str(x / self.screen.width)}% finished. x: {x}, y {y}')
                curr_ray: Ray = self.camera.get_cam_space_ray_at_pixel(x, y, self.screen.width, self.screen.width, 1)

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

                        if math_helper.ray_triangle_intersection(curr_ray, camera_space_vertices[0], camera_space_vertices[1], camera_space_vertices[2],0, 100):
                            print("hit!")
                            print(f"ray for x: {x} y: {y} is ray with dir: {str(curr_ray.direction)} at origin: {str(curr_ray.origin)}")
                            image_buffer_l[x, y] = (255, 0, 0)

        print("drawing buffer")
        self.screen.draw(image_buffer_l)

"""
def thread_function(x: int, y: int, renderer: Renderer):

    print("doing thread function", flush=True)

    logging.info("doing thread function")

    curr_ray: Ray = renderer.camera.get_cam_space_ray_at_pixel(x, y, renderer.screen.width, renderer.screen.width, 1)

    # check every triangle in scene
    for mesh in renderer.meshes:
        for face_index, face in enumerate(mesh.faces):
            face_normal = mesh.normals[face_index]

            # let's try to do this in camera space to avoid ray -> world space complications
            world_space_vertices: list = []
            camera_space_vertices: list = []

            for index in face:
                w_vert = mesh.transform.apply_to_point(mesh.verts[index])
                world_space_vertices.append(w_vert)

                c_vert = renderer.camera.project_point(w_vert)
                camera_space_vertices.append(c_vert)

            if math_helper.ray_triangle_intersection(curr_ray,
                                                     camera_space_vertices[0],
                                                     camera_space_vertices[1],
                                                     camera_space_vertices[2],
                                                     0, 100):
                print("hit!", flush=True)
                print(f"ray for x: {x} y: {y} is ray with dir: {str(curr_ray.direction)} at origin: {str(curr_ray.origin)}")
                renderer.set_image_buffer(x, y, (255, 0, 0))
"""