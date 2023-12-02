import numpy as np

from screen import Screen
from camera import PerspectiveCamera,OrthoCamera
from mesh import Mesh
from renderer import Renderer
from light import PointLight



if __name__ == '__main__':
    screen = Screen(200, 200)

    camera = OrthoCamera(-1.0, 1.0, -1.0, 1.0, 1, 60)
    # camera = PerspectiveCamera(-1.0, 1.0, -1.0, 1.0, 1, 60)
    # camera = PerspectiveCamera.from_FOV(45, 1, 60, 1)
    # camera = PerspectiveCamera(-1.0, 1.0, -1.0, 1.0, 1.0, 10)

    camera.transform.set_position(0, 0, 0)

    mesh = Mesh.from_stl("unit_sphere.stl", np.array([1.0, 0.0, 1.0]),\
        np.array([1.0, 1.0, 1.0]),0.0,1.0,1.0,100.0)
    mesh.transform.set_rotation(0, 0, 0)
    mesh.transform.set_position(0, 3, 0)

    # mesh2 = Mesh.from_stl("unit_sphere.stl", np.array([0.0, 1.0, 0.0]), \
    #                      np.array([1.0, 1.0, 1.0]), 0.2, 1.0, 0.0, 100)
    # mesh2.transform.set_position(0, 5, 0)

    light = PointLight(50.0, np.array([1, 1, 1]))
    light.transform.set_position(0, -1, -1)

    renderer = Renderer(screen, camera, [mesh], light)
    renderer.render("barycentric",[80,80,80], [0.1, 0.1, 0.1])

    screen.show()
