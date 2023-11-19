import numpy as np

from screen import Screen
from camera import PerspectiveCamera,OrthoCamera
from mesh import Mesh
from renderer import Renderer
from light import PointLight



if __name__ == '__main__':
    screen = Screen(500,500)

    camera = OrthoCamera(-2.0, 2.0, -2.0, 2.0, 1.0, 20)

    mesh_1 = Mesh.from_stl("suzanne.stl", np.array([1.0, 0.0, 1.0]),\
        np.array([1.0, 1.0, 1.0]),0.05,1.0,0.2,100)
    mesh_1.transform.set_rotation(-10, 0, 220)
    mesh_1.transform.set_position(-0.5, 2, 0)

    mesh_2 = Mesh.from_stl("unit_cube.stl", np.array([0.6, 0.0, 1.0]),\
        np.array([1.0, 1.0, 1.0]),0.05,1.0,0.2,100)
    mesh_2.transform.set_rotation(25, 0, 220)
    mesh_2.transform.set_position(1, 3.5, 0.5)


    light = PointLight(50.0, np.array([1, 1, 1]))
    light.transform.set_position(-4, -4, -3)

    renderer = Renderer(screen, camera, [mesh_1,mesh_2], light)
    renderer.render("depth",[15,15,15], [0.2, 0.2, 0.2])

    screen.show()