import light
from mesh import Mesh
from ray import Ray
from screen import Screen
from camera import PerspectiveCamera, OrthoCamera

import numpy as np
import math_helper
from vector import Vector3


class Renderer:

    def __init__(self, screen: Screen, camera, meshes: list[Mesh], light_):
        self.screen = screen
        self.camera = camera
        self.meshes = meshes
        self.light = light_

    def render(self, shading, bg_color: list, ambient_light) -> None:

        image_buffer: np.array = np.full((self.screen.width, self.screen.height, 3), bg_color)

        for x in range(0, self.screen.width):

            if x % (self.screen.width / 20):
                print(str(x / self.screen.width) + "% finished")

            for y in range(0, self.screen.height):

                curr_ray: Ray = self.camera.get_cam_space_ray_at_pixel(x, y, self.screen.width, self.screen.width, 1)
                curr_ray_w: Ray = self.camera.project_ray(curr_ray)

                # print(f"ray for x: {x} y: {y} is ray with dir: {str(curr_ray.direction)} at origin: {str(curr_ray.origin)}")

                # check every triangle in scene
                for mesh in self.meshes:
                    for face_index, face in enumerate(mesh.faces):
                        face_normal = mesh.normals[face_index]

                        # DO THIS IN WORLD SPACE

                        world_space_vertices: list = []
                        # screen_space_vertices: list = []

                        for index in face:
                            w_vert = mesh.transform.apply_to_point(mesh.verts[index])
                            world_space_vertices.append(Vector3.from_np_array(w_vert))

                            # s_vert = self.camera.project_point(w_vert)
                            # screen_space_vertices.append(Vector3.from_np_array(s_vert))
                            # print()

                        if math_helper.ray_triangle_intersection(curr_ray_w,
                                                                 world_space_vertices[0],
                                                                 world_space_vertices[1],
                                                                 world_space_vertices[2],
                                                                 0, 10000):
                            print("hit!")
                            image_buffer[x, y] = (255, 0, 0)

        print("drawing buffer")
        self.screen.draw(image_buffer)
