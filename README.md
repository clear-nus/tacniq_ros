# TACNIQ-ROS
This repository contains ROS scripts to connect and visualize tacniq sensors. Tested on Melodic.

## Prerequisits

1. Install tacniq driver using sudo priviligies:

``sudo bash tac_linux_driver.sh``

2. Make sure required python packages are installed: ``requirements.txt``

## How to run

1. Connect to the sensor:

``rosrun tacniq_ros tacniq_connect.py ``

Note: there are two publishers ``tacniq/left`` and ``tacniq/right``.

2. Visualize:

``rosrun tacniq_ros visualize.py``

## License 

``tacniq-ros`` is released under the MIT license.