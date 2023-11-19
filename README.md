[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/wFwLc0Zx)
# Programming Assignment 6

Class: COMPSCI 459(G)

Professor: Jerald Thomas

## Overview

In this programming assignment, you are going to complete the sixth step needed to render a 3D mesh, shading! You will be extending the render loop in `Renderer` to compute `flat` and `barycentric` shading, which requires the addition of a `PointLight` class and modifications to `Mesh` to include material properties. The `Renderer` class will finally be able to render multiple 3D objects with lighting!

## Instructions
To begin, you will extend the renderer module created in the last assignment by updating the inputs to the `render` function that account for `shading` type, `ambient_light` in the scene, and a list of `meshes` instead of a single `mesh`. Next, you will create the `PointLight` class within `light.py` to define a simple point light and update `Mesh` to be include members representing the material properties necessary for lighting computation. Even though specular components are not calcuated in this assignment, you are expected to add them to your `Mesh` class. The template code will include them as inputs when constructing a mesh using `from_stl()`. They will then be available for the Shading 2 assignment without any additional updates to the `Mesh` class. 

For this assignment, we will implement flat shading as the `flat` rendering mode, in which the normal from each triangle is used to compute lighting at each fragment/pixel. Only the lambertian (diffuse) lighting term needs to be computed for this assignment. Note, a simple approximation of the attenuation factor term can be division by the distance to the light squared. Your shading implemention should make use of the normal direction to cull back faces of each mesh. The depth value after projection should be used for depth clipping, by only rendering surface points that are within the bounds of -1 and 1, i.e., between the near and far planes. You must also maintain a z-buffer by keeping track of the depth value after projection. The depth value should be interpolated along each fragment using barycentric coordinates and is used to check whether the current surface is occluded by a closer object or not. Your depth buffer should be initialized to the same size as the screen with values of negative infinity or some large negative number. You should skip rendering surface points where the z values are less than what is currently stored in the buffer for our coordinate system. 

You will also implement a `barycentric` shading mode for the `render()` function. For each triangle, three vertices define the face within the face list `mesh.faces`. For this shading mode, the first vertex in this list should be assigned the value red, the second vertex green, and the third vertex blue. You will then use barycentric coordinates to interpolate between the vertex colors for shading each pixel. The result of this shading mode is useful for validating the ordering of vertices within your face list. Properly ordered vertices for our pipeline would show a counter-clockwise ordering of the red, green, and blue vertices. 

This assignment will make use of visual checks checks to validate your solutions.

TIP: It is easy to accidentally initialize a z-buffer with an integer (i.e., np.full((self.screen.height, self.screen.width), integer value)) and if so, the buffer will be round any values set with floats to the nearest integer, which will cause artifacts in rendering. 

TIP: The extra credit depth shader and the barycentric shader are very useful debugging tools, and it may be 
beneficial to implement those before tackling flat shading (they are also easier to implement)



### Output

There are a total of 8 scripts that can be executed. `extracredit.py` is what will be run to evaluate the extra credit. The scripts are: `assignment6_perspective_1`, `assignment6_perspective_2`, `assignment6_ortho_1`, `assignment6_ortho_2`, `assignment6_depth_1`, `assignment6_depth_2`, `assignment6_barycentric_1`, and `assignment6_barycentric_2`. The following image is a collage of running all of them:

![combined output](combined_output.png)

The scenes vary camera, mesh, and light position parameters and in some files include multiple objects with different depth orderings.

Note that these scripts require that the `PointLight` class has a `Transform` object (that defaults to no 
rotation or translation) member used to set the position and rotation of the light source.

### Dependency Management
Each assignment will include a requirements.txt file that includes the python package requirements for the assignment. If you are using PyCharm it should automatically detect and install the dependencies when you create the virtual environment. Otherwise, [these instructions](https://www.jetbrains.com/help/pycharm/managing-dependencies.html#configure-requirements) will help you manually manage the requirements in PyCharm. If you are using something other than PyCharm, you can use the command line to manually install the packages from the requirements.txt file:

```bash
pip install -r requirements.txt
```

## The `Light` class

### Exposed Members

#### `transform`
A `Transform` object exposed to set the orientation (position and rotation) of the camera. This should default to represent a position of `(0, 0, 0)` and no rotation.

#### `intensity`
A scalar value representing the intensity, or brightness of the light source.

#### `color`
A 3 element (RGB) array representing the color of the light source using values between `0.0` and `1.0`.

### Exposed Methods
There are no exposed methods.

## Update to the `Mesh` class

### Updated Methods

#### `__init__(self,diffuse_color,specular_color, ka, kd, ks, ke)`
The constructor now takes diffuse and specular color as an 3 element np array with all three values between `0.0` and `1.0`, as well as material properties `ka`, `kd`, `ks`, and `ke`.

#### `from_stl(stl_path,diffuse_color,specular_color, ka, kd, ks, ke)`
This static method takes an stl file as input, initializes an empty Mesh object using the input material properties `diffuse_color, specular_color, ka, kd, ks, ke` and populates the `verts`, `faces`, and `normals` member variables. The method returns the populated Mesh object.

## Update to the `Renderer` class

### Updated Methods

#### `__init__(self, screen, camera, meshes, light)`
The class constructor takes a screen object (of type `Screen`), camera object (either of type `OrthoCamera` or `PerspectiveCamera`), a list of mesh objects (of type `Mesh`), and a light source (of type `PointLight`) and stores them.

#### `render(self, shading, bg_color, ambient_light)`
This method will now take a three input arguments. `shading` is a string parameter indicating which type of shading to apply, for this assignment `flat` and `barycentric` should be implemented. `bg_color` is a three element list that is to be the background color of the render (that is, all of the pixels that are not part of a mesh). `ambient_light` defines the intensity and color of any ambient lighting to add within the scene. `render` will execute the basic render loop that we discussed in class and compute shading at each pixel fragment to update an image buffer. It will then draw that image buffer to  the `screen` object using the `screen.draw` method, but it will not run the pygame loop (the calling function will call `screen.show`)

## Extra Credit
Extra credit for this assignment will be to add a `depth` shading mode. This shader will color pixels in grayscale 
relative to their value within the z-buffer. In several of our scenes, the objects only occupy a small range of the 
overall z-buffer, so we will also scale the values relative to the objects in the scene. This can be accomplished by 
iterating over all of the vertices in the scene, converting them to screen space, and storing the minimum and 
maximum depth values (the +y values in our coordinate system). The shader output should color a pixel exactly black
([0, 0, 0]) if the fragment has a depth value of exactly the minimum depth value, and should color a pixel exactly 
white ([255, 255, 255]) if the fragment has a depth value of exactly the maximum depth value. For all values 
inbetween, the pixel should be a gray-scale interpolation. The extra credit will be validated by running 
`extracredit.py` and comparing the resulting rendering with the expected output below.


![extra credit output](extracredit_output.png)



## Rubric
There are 20 points (22 with extra credit) for this assignment:
- *16 pts*: The flat shaded renderings produced from the assignment_* scripts are rendered as expected.
  - *2 pts*: `assignment6_perspective_1`
  - *2 pts*: `assignment6_perspective_2`
  - *2 pts*: `assignment6_ortho_1`
  - *2 pts*: `assignment6_ortho_2`
  - *4 pts*: `assignment6_depth_1`
  - *4 pts*: `assignment6_depth_2`
- *4 pts*:  The barycentric shading renderings of the cube and Suzanne are rendered as expected.
  - *2 pts*: `assignment6_barycentric_1`
  - *2 pts*: `assignment6_barycentric_2`

