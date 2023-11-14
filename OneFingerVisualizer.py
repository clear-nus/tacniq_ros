from __future__ import division, print_function, absolute_import

import numpy as np
import pygame

import re
import sys
import threading
import time
from tactileSensor import TactileSensor

fingerL = TactileSensor(productID= 0x0100)

grid_size = 60
grid_margin = 0

# window_width = (2 * fingerL.sensorArrayWidth + 1) * (grid_size + grid_margin) - grid_margin
window_width = (fingerL.sensorArrayWidth + 1) * (grid_size )-55
window_height = fingerL.sensorArrayHeight * (grid_size + grid_margin) - grid_margin

def drawData(screen, font, data, is_left=True):
    
    for i in range(fingerL.sensorArrayWidth):
        for j in range(fingerL.sensorArrayHeight):

            if is_left:
                center_x = (i + 1) * (grid_size + grid_margin) - grid_margin - (grid_size / 2)
            else:
                center_x = (i + fingerL.sensorArrayWidth + 2) * (grid_size + grid_margin) - grid_margin - (grid_size / 2)

            center_y = (j + 1) * (grid_size + grid_margin) - grid_margin - (grid_size / 2)

            adjusted_value = 1 - (data[j][i] / fingerL.maxValue)
            adjusted_size = (grid_size - 10) + 10 * adjusted_value
            adjusted_bg_color = lerp_color((128, 255, 219), (116, 0, 184), adjusted_value)
            adjusted_fg_color = lerp_color((0, 0, 0), (255, 255, 255), adjusted_value)
            # if adjusted_value < 0.05:
            #     adjusted_fg_color = (86, 207, 225)

            grid_rect = pygame.Rect(center_x, center_y, adjusted_size, adjusted_size)
            grid_rect.center = (center_x, center_y)
            pygame.draw.rect(screen, adjusted_bg_color, grid_rect)

            text = font.render(f"{data[j][i]}", True, adjusted_fg_color)
            text_rect = text.get_rect(center=grid_rect.center)
            
            screen.blit(text, text_rect)

def lerp(start, end, t):
    return start + (end - start) * t

def lerp_color(start, end, t):
    return (lerp(start[0], end[0], t), lerp(start[1], end[1], t), lerp(start[2], end[2], t))

def main():

    global data_l, data_r, running
    running = True
    
    # The next few lines of code is run once before looping the exact same thing... I forgot why I did this.
    # Gets sensor data array
    data_l = fingerL.getDataAll()

    # The next two lines of code flips the visualizer to show it right-side-up
    data_l = np.flip(data_l,0)
    data_l = np.flip(data_l,1)

    def readDataLeft():
        global data_l
        while running:
            time.sleep(1 / 30)
            data_l = fingerL.getDataAll()
            data_l = np.flip(data_l,0)
            data_l = np.flip(data_l,1)
    
    thread_l = threading.Thread(target=readDataLeft)

    thread_l.start()

    # # setup visualization
    pygame.init()
    pygame.display.set_caption("Tactile Sensor Display")
    screen = pygame.display.set_mode([window_width, window_height])
    font = pygame.font.SysFont("Manjari", 18)

    # running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        screen.fill((255, 255, 255))
        drawData(screen, font, data_l, is_left=True)
        # drawData(screen, font, data_r, is_left=False)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()