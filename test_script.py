import numpy as np

from screen import Screen
from camera import PerspectiveCamera,OrthoCamera
from mesh import Mesh
from renderer import Renderer
from light import PointLight



if __name__ == '__main__':
    screen = Screen(500, 500)

    # camera = OrthoCamera(-1.0, 1.0, -1.0, 1.0, 1, 60)
    # camera = PerspectiveCamera(-1.0, 1.0, -1.0, 1.0, 1, 60)
    camera = PerspectiveCamera.from_FOV(45, 1, 60, 1)
    # camera = PerspectiveCamera(-1.0, 1.0, -1.0, 1.0, 1.0, 10)
    camera.transform.set_position(0, -6, 3)
    camera.transform.set_rotation(-25, 0, 0)

    mesh = Mesh.from_stl("unit_sphere.stl", np.array([171.0 / 255.0, 132.0 / 255.0, 32.0 / 255.0]),\
        np.array([1.0, 1.0, 1.0]),0.2,0.7,0.3,50.0, 0.05, False)
    mesh.transform.set_position(0, 0, 0.5)

    mesh2 = Mesh.from_stl("unit_cube.stl", np.array([7.0 / 255.0, 20.0 / 255.0, 32.0 / 255.0]), \
                         np.array([1.0, 1.0, 1.0]), 0.2, 0.7, 0.3, 1.0, 0.05, True)
    mesh2.transform.set_rotation(0, 0, 45)
    mesh2.transform.set_position(-1.6, -1, 0)

    mesh3 = Mesh.from_stl("unit_cube.stl", np.array([161.0 / 255.0, 24.0 / 255.0, 58.0 / 255.0]), \
                         np.array([1.0, 1.0, 1.0]), 0.2, 0.7, 0.3, 1.0, 0.05, True)
    mesh3.transform.set_position(1.6, -1, 0)

    floor_mesh = Mesh.from_stl("flat_cube.stl", np.array([1.0, 1.0, 1.0]), \
                          np.array([1.0, 1.0, 1.0]), 0.4, 1.0, 0.0, 1.0, 0.05, True)
    floor_mesh.transform.set_position(0, 0, -1)



    light = PointLight(15.0, np.array([1, 1, 1]))
    light.transform.set_position(-3, -3, 2)

    renderer = Renderer(screen, camera, [mesh, mesh2, mesh3, floor_mesh], light)
    renderer.render("barycentric",[80,80,80], [0.1, 0.1, 0.1])

    screen.show()
