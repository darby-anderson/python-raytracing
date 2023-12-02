

class RayTriangleIntersectionResult:

    def __init__(self, hit: bool, t: float, theta: float, beta: float):
        self.hit = hit
        self.t = t
        self.theta = theta # about C ?
        self.beta = beta # about B ?
        self.alpha = (1 - beta) - theta # about A ?
