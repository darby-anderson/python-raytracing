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

    def __init__(self, diffuse_color: np.array, specular_color: np.array, ka: float, kd: float, ks: float, ke: float, km: float, hard_edges: bool):
        self.faces = []
        self.normals = []
        self.verts = []
        self.vertex_normals = []

        self.diffuse_color: np.array = diffuse_color
        self.specular_color: np.array = specular_color
        self.ka: float = ka
        self.kd: float = kd
        self.ks: float = ks
        self.ke: float = ke
        self.km: float = km

        self.hard_edges = hard_edges

        self.material = Material(ka, kd, diffuse_color, ks, specular_color, ke, km)

        self.aabb_smallest_point_world = np.array([0, 0, 0])
        self.aabb_greatest_point_world = np.array([0, 0, 0])

        self.transform = Transform()

        self.calced_aabb_box = False

    def hit(self, ray: Ray, t_min: float, t_max: float) -> (bool, HitRecord):

        if not self.calced_aabb_box:
            self.calc_aabb_box()
            self.calced_aabb_box = True

        if not math_helper.ray_aabb_intersection(ray, self.aabb_smallest_point_world, self.aabb_greatest_point_world):
            # print("rejecting from AABB miss")
            return False, None

        # print("got here")

        hit_record = None
        face_hit: bool = False
        lowest_t: float = t_max + 1

        for face_index, face in enumerate(self.faces):
            face_normal = self.normals[face_index]
            face_normal_world = math_helper.get_normalized(self.transform.apply_to_normal(face_normal))

            # check if hitting back of face
            if math_helper.dot(face_normal_world, ray.direction) > 0:
                # hitting the back of the face
                # print("rejecting from back face")
                continue

            # let's try to do this in camera space to avoid ray -> world space complications

            world_space_vertices: list = []
            world_space_normals: list = []

            for index in face:
                w_vert = self.transform.apply_to_point(self.verts[index])
                world_space_vertices.append(w_vert)

                w_vert_normal = self.transform.apply_to_normal(self.vertex_normals[index])
                world_space_normals.append(w_vert_normal)

            # print(f'w_s_verts: {str(world_space_vertices)}')

            result: RayTriangleIntersectionResult = math_helper.ray_triangle_intersection(ray, world_space_vertices[0], world_space_vertices[1], world_space_vertices[2], t_min, t_max)

            if self.hard_edges:
                normal_w = face_normal_world
            else:
                normal_w: np.array = math_helper.get_normalized(world_space_normals[0] * result.alpha + world_space_normals[1] * result.beta +
                                               world_space_normals[2] * result.theta)

            if result.hit and result.t < lowest_t:
                lowest_t = result.t
                face_hit = True
                point_hit = ray.at(result.t)
                hit_record = HitRecord(point_hit, face_normal_world, result, normal_w, self.material)

        return face_hit, hit_record

    def calc_aabb_box(self):
        large_num: float = 100000.0
        small_num: float = -100000.0
        aabb_smallest_point: np.array = np.array([large_num, large_num, large_num])
        aabb_greatest_point: np.array = np.array([small_num, small_num, small_num])

        world_space_vertices: list = []
        for vert in self.verts:
            nw_vert = self.transform.apply_to_point(vert)
            world_space_vertices.append(nw_vert)
            # print(f'original vert: {vert} nw_vert: {nw_vert}')

        for w_vert in world_space_vertices:
            # SMALLEST
            if w_vert[0] < aabb_smallest_point[0]:
                aabb_smallest_point[0] = w_vert[0]

            if w_vert[1] < aabb_smallest_point[1]:
                aabb_smallest_point[1] = w_vert[1]

            if w_vert[2] < aabb_smallest_point[2]:
                aabb_smallest_point[2] = w_vert[2]

            # GREATEST
            if w_vert[0] > aabb_greatest_point[0]:
                aabb_greatest_point[0] = w_vert[0]

            if w_vert[1] > aabb_greatest_point[1]:
                aabb_greatest_point[1] = w_vert[1]

            if w_vert[2] > aabb_greatest_point[2]:
                aabb_greatest_point[2] = w_vert[2]

        print("smallest point: " + str(aabb_smallest_point))
        print("greatest point: " + str(aabb_greatest_point))

        # copy vertices from vert_list
        self.aabb_smallest_point_world = aabb_smallest_point
        self.aabb_greatest_point_world = aabb_greatest_point

    @staticmethod
    def from_stl(stl_path, diffuse_color: np.array, specular_color: np.array, ka: float, kd: float, ks: float,
                 ke: float, km: float, hard_edges: bool):
        my_mesh: Mesh = Mesh(diffuse_color, specular_color, ka, kd, ks, ke, km, hard_edges)
        stl_mesh: mesh.Mesh = mesh.Mesh.from_file(stl_path)

        num_faces = len(stl_mesh.points)

        vert_list = []
        temp_faces = np.zeros((num_faces, 3), dtype=int)
        temp_normals = np.zeros((num_faces, 3))

        vert_normal_dict: dict[int, list[np.array]] = {}

        for face_index, face in enumerate(stl_mesh.points):

            face_normal = stl_mesh.normals[face_index]
            temp_normals[face_index] = face_normal

            verts = [np.array(face[0:3]), np.array(face[3:6]), np.array(face[6:9])]

            for vert_index, vertex in enumerate(verts):

                # check if vertex is in vert_list
                index = -1
                for existing_index, existing_vert in enumerate(vert_list):
                    if math_helper.check_if_vectors_identical(existing_vert, vertex):
                        index = existing_index
                        vert_normal_dict[index].append(np.array(face_normal))
                        break

                if index == -1:  # get new index if not found
                    index = len(vert_list)
                    vert_list.append(vertex.tolist())
                    vert_normal_dict[index] = [np.array(face_normal)]

                temp_faces[face_index][vert_index] = index

        vert_normals = []

        for index, vert in enumerate(vert_list):
            normals = vert_normal_dict[index]
            normal_sum = np.array([0.0, 0.0, 0.0])
            for normal in normals:
                normal_sum += normal

            vert_normals.append(math_helper.get_normalized(normal_sum))

        # copy vertices from vert_list
        my_mesh.verts = vert_list
        my_mesh.vertex_normals = vert_normals
        my_mesh.faces = temp_faces.tolist()
        my_mesh.normals = temp_normals.tolist()

        return my_mesh