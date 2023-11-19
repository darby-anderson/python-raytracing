import numpy as np
from stl import mesh
import math_helper
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

        self.transform = Transform()

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

        # copy vertices from vert_list
        my_mesh.verts = vert_list
        my_mesh.faces = temp_faces.tolist()
        my_mesh.normals = temp_normals.tolist()

        return my_mesh
