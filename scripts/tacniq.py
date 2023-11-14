#!/usr/bin/env python

import numpy as np
import rospy
from std_msgs.msg import Int16MultiArray, MultiArrayDimension
import usb
import re

class Tacniq(object):
    def __init__(self):
        def activate(id_product):
            dev = usb.core.find(idVendor=0x2fe3, idProduct=id_product)
            if dev is None:
                return None
            if dev.is_kernel_driver_active(0):
                try:
                    dev.detach_kernel_driver(0)
                except usb.core.USBError as e:
                    return None
            return dev
        self.devL = activate(id_product=0x0100)
        self.devR = activate(id_product=0x0102)
        success = True
        if self.devL is None:
            rospy.logerror("Left finger not found")
            success = False
        if self.devR is None:
            rospy.logerror("Right finger not found")
            success = False
        if not success:
            raise ValueError('Cannot access one of the fingers')
        rospy.loginfo("Init done")

        self.devL.set_configuration()
        self.devR.set_configuration()
        self.max_adc_value = 3500

        self.left_publisher = rospy.Publisher("tacniq/left", Int16MultiArray, queue_size=1)
        self.right_publisher = rospy.Publisher("tacniq/right", Int16MultiArray, queue_size=1)

    def read_device(self, device):
        data_pt1 = device.read(0x81, 64, 100)
        data_pt2 = None
        if len(data_pt1) == 64:
            data_pt2 = device.read(0x81, 38, 100)
        if data_pt2 is not None:
            hex_placeholder = []
            data = data_pt1 + data_pt2
            for dec in data:
                hex_placeholder.append("{:02x}".format(dec))
            hex_placeholder = "".join(hex_placeholder)
            hex_data = re.findall('...', hex_placeholder)
            adc_data = list(map(lambda hex_val: int(hex_val, 16), hex_data))
            map_data = np.array([[0, adc_data[31], adc_data[22], adc_data[40], adc_data[2], 0], 
                    [adc_data[63],adc_data[26],adc_data[24],adc_data[6],adc_data[4],adc_data[0]],
                    [adc_data[51],adc_data[27],adc_data[49],adc_data[14],adc_data[41],adc_data[13]],
                    [adc_data[16],adc_data[53],adc_data[17],adc_data[46],adc_data[42],adc_data[45]],
                    [adc_data[23],adc_data[62],adc_data[57],adc_data[38],adc_data[33],adc_data[1]],
                    [adc_data[29],adc_data[59],adc_data[19],adc_data[11],adc_data[5],adc_data[3]],
                    [adc_data[28],adc_data[20],adc_data[56],adc_data[39],adc_data[10],adc_data[35]],
                    [adc_data[21],adc_data[55],adc_data[54],adc_data[7],adc_data[8],adc_data[12]],
                    [adc_data[30],adc_data[58],adc_data[18],adc_data[47],adc_data[36],adc_data[32]],
                    [adc_data[61],adc_data[25],adc_data[48],adc_data[15],adc_data[37],adc_data[34]],
                    [adc_data[60],adc_data[52],adc_data[50],adc_data[44],adc_data[43],adc_data[9]]])
            return map_data

    def sensor_data2ros(self, data):
        msg = Int16MultiArray()
        msg.layout.dim.append(MultiArrayDimension())
        msg.layout.dim.append(MultiArrayDimension())
        msg.layout.dim[0].size = 11
        msg.layout.dim[0].label = "height"
        msg.layout.dim[1].size = 6
        msg.layout.dim[1].label = "width"
        msg.layout.dim[0].stride = 11 * 6
        msg.layout.dim[1].stride = 6
        msg.data = data.flatten()
        return msg

    def run(self):
        left_data = self.max_adc_value - self.read_device(self.devL)
        right_data = self.max_adc_value - self.read_device(self.devR)
        self.left_publisher.publish(self.sensor_data2ros(left_data))
        self.right_publisher.publish(self.sensor_data2ros(right_data))

if __name__=='__main__':
    rospy.init_node('tacniq_ros')
    tacniq_sensor = Tacniq()
    while not rospy.is_shutdown():
        tacniq_sensor.run()
    rospy.spin()
