#!/usr/bin/env python

import numpy as np
import rospy
from std_msgs.msg import Int16MultiArray, MultiArrayDimension
import matplotlib.pyplot as plt
from matplotlib import animation

max_adc_value = 3500  # max adc value depends on FPGA
tac_map_height = 11
tac_map_width = 6


left_image = np.ones([tac_map_height, tac_map_width])*max_adc_value
right_image = np.ones([tac_map_height, tac_map_width])*max_adc_value


def read_left_tacniq(msg):
    global left_image
    left_image = read_tacniq_data(msg)

def read_right_tacniq(msg):
    global right_image
    right_image = read_tacniq_data(msg)

def read_tacniq_data(msg):
    data_flattened = np.array(msg.data)
    height = msg.layout.dim[0].size
    width = msg.layout.dim[1].size
    data = data_flattened.reshape([height,width])
    return data

# left_image, right_image = get_data()

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(25, 25))  # initializing the figure
# fig.canvas.set_window_title('Visualizer: Tactile Images')
fig.patch.set_facecolor('white')
cmap = 'Blues'
# im = ax.imshow(right_image, vmin=0, vmax=max_adc_value, cmap=cmap)
im0 = ax[0].imshow(left_image, vmin=0, vmax=max_adc_value, cmap=cmap)
im1 = ax[1].imshow(right_image, vmin=0, vmax=max_adc_value, cmap=cmap)
# plt.colorbar(im0, ax=ax[1])  # color legend
# plt.colorbar(im, ax=ax)  # color legend0

all_artists = []
all_artists.append(im0)
all_artists.append(im1)

ax[0].set_xticks([])
ax[0].set_yticks([])
ax[0].set_title('Left', fontsize=30)
ax[1].set_xticks([])
ax[1].set_yticks([])
ax[1].set_title('Right', fontsize=30)

texts0 = [[None] * tac_map_height for _ in range(tac_map_width)]
texts1 = [[None] * tac_map_height for _ in range(tac_map_width)]

for x in range(tac_map_width):
    for y in range(tac_map_height):
        texts0[x][y] = ax[0].text(x, y, '', fontsize=16, ha='center', va='center')
        texts1[x][y] = ax[1].text(x, y, '', fontsize=16, ha='center', va='center')
        all_artists.append(texts0[x][y])
        all_artists.append(texts1[x][y])

def init():  # initialize the tactile map: ADC values
    global im0, im1, texts0, texts1, all_artists, left_image, right_image

    
    im0.set_array(left_image)
    im1.set_array(right_image)

    for x in range(tac_map_width):
        for y in range(tac_map_height):
            # texts0[x][y].set_text(int(left_image[y,x]))
            if left_image[y,x] < 2500:
                texts0[x][y].set_color("black")
            else:
                texts0[x][y].set_color("white")

            # texts1[x][y].set_text(int(right_image[y,x]))
            if right_image[y,x] < 2500:
                texts1[x][y].set_color("black")
            else:
                texts1[x][y].set_color("white")
    return all_artists

def animate(i):  # this function is called sequentially
    global im0, im1, texts0, texts1, all_artists, left_image, right_image
  
    im0.set_array(left_image)
    im1.set_array(right_image)
    for x in range(tac_map_width):
        for y in range(tac_map_height):
            # texts0[x][y].set_text(int(left_image[y,x]))
            if left_image[y,x] < 2500:
                texts0[x][y].set_color("black")
            else:
                texts0[x][y].set_color("white")

            # texts1[x][y].set_text(int(right_image[y,x]))
            if right_image[y,x] < 2500:
                texts1[x][y].set_color("black")
            else:
                texts1[x][y].set_color("white")
    return all_artists

if __name__ == '__main__':
    rospy.init_node("tacniq_visualizer")
    rospy.Subscriber('tacniq/left', Int16MultiArray, read_left_tacniq)
    rospy.Subscriber('tacniq/right', Int16MultiArray, read_right_tacniq)
    anim = animation.FuncAnimation(fig, animate, init_func=init, interval=0, blit=True)
    plt.show()
    