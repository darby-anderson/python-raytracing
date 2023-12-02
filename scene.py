from hit_record import HitRecord
from mesh import Mesh
from ray import Ray


class Scene:

    def __init__(self, meshes: list[Mesh]):
        self.meshes = meshes

    def hit(self, ray: Ray, t_min: float, t_max: float) -> (bool, HitRecord):

        lowest_t: float = t_max + 1
        hit_an_object: bool = False
        closest_obj_hit_record = None

        for mesh in self.meshes:
            was_hit, hit_record = mesh.hit(ray, t_min, t_max)

            if was_hit and hit_record.intersection_result.t < lowest_t:
                hit_an_object = True
                closest_obj_hit_record = hit_record

        return hit_an_object, closest_obj_hit_record
