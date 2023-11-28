import sys

import numpy as np
from stl import mesh
import math_helper
from hit_record import HitRecord
from material import Material
from ray import Ray
from ray_triangle_intersection_result import RayTriangleIntersectionResult
from transform import Transform


class Mesh:

    def __init__(self, diffuse_color: np.array, specular_color: np.array, ka: float, kd: float, ks: float, ke: float):
        self.faces = []
        self.normals = []
        self.verts = []

        self.diffuse_color: np.array = diffuse_color
        self.specular_color: np.array = specular_color
        self.ka: float = ka
        self.kd: float = kd
        self.ks: float = ks
        self.ke: float = ke

        self.material = Material(ka, kd, diffuse_color, ks, specular_color, ke)

        self.aabb_smallest_point = np.array([0, 0, 0])
        self.aabb_greatest_point = np.array([0, 0, 0])

        self.transform = Transform()

    def hit(self, ray: Ray, t_min: float, t_max: float) -> (bool, HitRecord):

        smallest_point_in_world = self.transform.apply_to_point(self.aabb_smallest_point)
        largest_point_in_world = self.transform.apply_to_point(self.aabb_greatest_point)

        if not math_helper.ray_aabb_intersection(ray, smallest_point_in_world, largest_point_in_world):
            # print("rejecting from AABB miss")
            return False, None

        for face_index, face in enumerate(self.faces):
            face_normal = self.normals[face_index]

            # check if hitting back of face
            if math_helper.dot(face_normal, ray.direction) > 0:
                # hitting the back of the face
                continue

            # let's try to do this in camera space to avoid ray -> world space complications

            world_space_vertices: list = []

            for index in face:
                w_vert = self.transform.apply_to_point(self.verts[index])
                world_space_vertices.append(w_vert)

            result: RayTriangleIntersectionResult = math_helper.ray_triangle_intersection(ray, world_space_vertices[0], world_space_vertices[1], world_space_vertices[2], t_min, t_max)

            if result.hit:
                # print('hit')
                point_hit = ray.at(result.t)
                hit_record = HitRecord(point_hit, face_normal, result.t, self.material)
                return True, hit_record

        return False, None

    @staticmethod
    def from_stl(stl_path, diffuse_color: np.array, specular_color: np.array, ka: float, kd: float, ks: float, ke: float):
        my_mesh: Mesh = Mesh(diffuse_color, specular_color, ka, kd, ks, ke)
        stl_mesh: mesh.Mesh = mesh.Mesh.from_file(stl_path)

        num_faces = len(stl_mesh.points)

        vert_list = []
        temp_faces = np.zeros((num_faces, 3), dtype=int)
        temp_normals = np.zeros((num_faces, 3))

        for face_index, face in enumerate(stl_mesh.points):

            temp_normals[face_index] = stl_mesh.normals[face_index]

            verts = [np.array(face[0:3]), np.array(face[3:6]), np.array(face[6:9])]

            for vert_index, vertex in enumerate(verts):

                # check if vertex is in vert_list
                index = -1
                for existing_index, existing_vert in enumerate(vert_list):
                    if math_helper.check_if_vectors_identical(existing_vert, vertex):
                        index = existing_index
                        break

                if index == -1:  # get new index if not found
                    index = len(vert_list)
                    vert_list.append(vertex.tolist())

                temp_faces[face_index][vert_index] = index

        large_num: float = 100000.0
        small_num: float = -100000.0
        aabb_smallest_point: np.array = np.array([large_num, large_num, large_num])
        aabb_greatest_point: np.array = np.array([small_num, small_num, small_num])

        for vert in vert_list:
            # SMALLEST
            if vert[0] < aabb_smallest_point[0]:
                aabb_smallest_point[0] = vert[0]

            if vert[1] < aabb_smallest_point[1]:
                aabb_smallest_point[1] = vert[1]

            if vert[2] < aabb_smallest_point[2]:
                aabb_smallest_point[2] = vert[2]

            # GREATEST
            if vert[0] > aabb_greatest_point[0]:
                aabb_greatest_point[0] = vert[0]

            if vert[1] > aabb_greatest_point[1]:
                aabb_greatest_point[1] = vert[1]

            if vert[2] > aabb_greatest_point[2]:
                aabb_greatest_point[2] = vert[2]

        print("smallest point: " + str(aabb_smallest_point))
        print("greatest point: " + str(aabb_greatest_point))

        # copy vertices from vert_list
        my_mesh.aabb_smallest_point = aabb_smallest_point
        my_mesh.aabb_greatest_point = aabb_greatest_point
        my_mesh.verts = vert_list
        my_mesh.faces = temp_faces.tolist()
        my_mesh.normals = temp_normals.tolist()

        return my_mesh
