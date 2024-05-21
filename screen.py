import datetime
import string

import numpy as np
import pygame
pygame.init()


class Screen:

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.surface = pygame.display.set_mode([width, height])

    def ratio(self):
        return self.width / self.height

    def do_capture(self):
        file_name: string = f'{str(datetime.datetime.now().time())[0:5]}.png'
        file_name = file_name.replace(":", "h")
        print(file_name)
        pygame.image.save(self.surface, file_name)

    def draw(self, buffer):
        if buffer.shape != (self.width, self.height, 3):
            raise Exception("Color buffer of wrong shape")

        buffer = np.fliplr(buffer)

        pygame.pixelcopy.array_to_surface(self.surface, buffer)

        pygame.display.flip()

    def show(self):
        # running = True
        # while running:
        #     for event in pygame.event.get():
        #         if event.type == pygame.QUIT:
        #             running = False

        pygame.quit()

    def screen_to_pixel(self, x, z) -> np.array:
        p_x = int((x + 1) * (self.width - 1) / 2)  # w - 1 to not overflow
        p_y = int((z + 1) * (self.height - 1) / 2)

        return np.array([p_x, p_y])

    def pixel_to_screen(self, x: int, y: int) -> np.array:
        s_x = ((2 * (x + 0.5)) / (self.width - 1)) - 1.0
        s_z = ((2 * (y + 0.5)) / (self.height - 1)) - 1.0

        return np.array([s_x, s_z])
