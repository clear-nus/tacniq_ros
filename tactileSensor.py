'''
TODO: 
- Line 77 make it so that it's flexible for different kinds of sensors.
'''
# This is a tactile sensor. Proper orientation when mounted on a gripper, faced down. 
# Dependencies:
# Cython
# python
# hdiapi
# pygame

# Helpful links for getting dependencies up and running for mac:
#     https://github.com/trezor/cython-hidapi
#     https://ports.macports.org/port/hidapi/
#     https://trezor.github.io/cython-hidapi/

# The sensor sends data in batches of 102 bytes.
# On ubuntu, we need to grab 64 bytes and then 38 bytes, cause the max we can grab at one shot on an ubuntu is 64.
# However, on a mac, all 102 bytes need to be grabbed in one shot, if not the data gets screwed up cause breaking the data into 64 and 38
# will somehow cause a random 0 element to appear between the 64 element array and 38 element array, and this will screw up the string formations.

import hid
import sys
import numpy as np
import re
import platform

class TactileSensor:
    def __init__(self, vendorID = 0x2fe3, productID = 0x0100,serialNumber = None, minValue = 0, maxValue = 4096, taxelThreshold = 500, minNumberOfTaxelsForTouch = 10, xOrigin = 0, yOrigin = 0, sensorArrayHeight = 11, sensorArrayWidth = 6):

        # Connect to sensor at init
        # self.__setUSBProperties(vendorID, productID) # input expected USB properties
        self.__setUSBProperties(vendorID, productID, serialNumber)
        self.setOS()
        self.setValueLimits(minValue, maxValue) # Set minimum expected sensor reading value and maximum sensor reading value
        self.setMinNumberForTouch(minNumberOfTaxelsForTouch) # Minimum number of activated taxels to consider as a touch.
        self.setTaxelThreshold(taxelThreshold) # Minimum ADC value to be considered as a trigger.
        self.setArrayDimensions(xOrigin, yOrigin, sensorArrayHeight, sensorArrayWidth) # crop array
        self.returnSetupValues()

        self.saturationCallbacks = []# array of callback functions
    
    ''' ####################################################
        Setting functions.
    #################################################### '''
    #Sets up usb from device PID, VID, and serial number.
    def __setUSBProperties(self, vendorID, productID, serialNumber):
        self.device = hid.device()
        
        if serialNumber is None: #Checks if serial number was provided as an input
            self.device.open(vendor_id = vendorID, product_id = productID)
        else: #In this case, serial number was provided.
            self.device.open(vendor_id = vendorID, product_id = productID, serial_number = serialNumber)
        if self.device is None:
            raise ValueError("Finger not found")
        
    #Checks OS and sets the appropriate data reading method based on OS.
    #Self.getDataAll method is declared in this method. I'd like to put it somewhere a little more visible but my IQ isnt high enough to figure out where else to put it.
    def setOS(self):
        self.operatingSystem = platform.system()
        if self.operatingSystem == "Windows" or self.operatingSystem == "Darwin":
            self.getDataAll = self.getDataAll_Windows_Mac #No brackets at the end because this is an assignmnet, not a function call.
        elif self.operatingSystem == "Linux":
            self.getDataAll = self.getDataAll_Ubuntu
        

    def setValueLimits(self, minValue, maxValue): # Set the min and max reading.
        #if no min value is declared, default to 0
        self.minValue = minValue
        self.maxValue = maxValue

    def setMinNumberForTouch(self, minNumberOfTaxelsForTouch): # Set the minimum number of activated taxels that will count as a touch
        self.minNumberOfTaxelsForTouch = minNumberOfTaxelsForTouch
        

    def setTaxelThreshold(self, taxelThreshold): # Set the minimum force reading required to count as activated
        self.taxelThreshold = taxelThreshold

    def setArrayDimensions(self, xOrigin, yOrigin, sensorArrayHeight, sensorArrayWidth): # Set the array coordinates and length and width
        self.xOrigin = xOrigin
        self.yOrigin = yOrigin
        self.sensorArrayHeight = sensorArrayHeight
        self.sensorArrayWidth = sensorArrayWidth
        self.sensorArrayTotalLength = sensorArrayHeight * sensorArrayWidth

    def setSlipSensitivity(self, filterArray): # Set the filter sensitivity. Input is the filter array? idk need to research more.
        pass

    ''' ####################################################
        Get values.
    #################################################### '''
    def getUSBDevice(self):
        return self.device
    
    def getDataAll_Ubuntu(self): # returns array of sensor values
        #Attempts to read 64 bytes from the sensor
        data1 = self.device.read(64,timeout_ms = 100)
        # If data read is not 64 bytes, read again. most likely incorrect length is 38, which is 102-64. 102 us the actual size of the payload, which needs to be broken into 64 + 38 for ubuntu. Mac and windows dont have this issue.
        if len(data1) < 64:
            data1 = self.device.read(64,timeout_ms = 100)
        assert len(data1) == 64
        # Read the remaining 38 bytes after the initial 64 bytes are read
        data2 = self.device.read(38,timeout_ms = 100)
        assert len(data2) is not None
        data = data1 + data2

        # I dont really know how these next few lines of code works, but it converts the sensor raw HID data array readings into readable format.
        hex_string = "".join(map(lambda dec: f"{dec:02x}", data))
        hex_data = re.findall("...", hex_string)
        adc_data = list(map(lambda hex: int(hex, 16), hex_data))

        #Hardcoded base array because it needs to follow the data format of the finger sensor
        #Should make this configurable in future
        baseArray = np.array([[0, adc_data[31], adc_data[22], adc_data[40], adc_data[2],0],
                    [adc_data[63], adc_data[26], adc_data[24], adc_data[6], adc_data[4], adc_data[0]],
                    [adc_data[51], adc_data[27], adc_data[49], adc_data[14], adc_data[41], adc_data[13]],
                    [adc_data[16], adc_data[53], adc_data[17], adc_data[46], adc_data[42], adc_data[45]],
                    [adc_data[23], adc_data[62], adc_data[57], adc_data[38], adc_data[33], adc_data[1]],
                    [adc_data[29], adc_data[59], adc_data[19], adc_data[11], adc_data[5], adc_data[3]],
                    [adc_data[28], adc_data[20], adc_data[56], adc_data[39], adc_data[10], adc_data[35]],
                    [adc_data[21], adc_data[55], adc_data[54], adc_data[7], adc_data[8], adc_data[12]],
                    [adc_data[30], adc_data[58], adc_data[18], adc_data[47], adc_data[36], adc_data[32]],
                    [adc_data[61], adc_data[25], adc_data[48], adc_data[15], adc_data[37], adc_data[34]],
                    [adc_data[60], adc_data[52], adc_data[50], adc_data[44], adc_data[43], adc_data[9]]])
        
        
        # crop sensor array height and width, starting from defined x and y origin. Remember, input is (HEIGHT, WIDTH)
        croppedArray = baseArray[self.yOrigin : (self.yOrigin + self.sensorArrayHeight), self.xOrigin : (self.xOrigin + self.sensorArrayWidth)]
        #print (self.yOrigin + self.sensorArrayHeight)
        #print(croppedArray)
        return croppedArray
    
    def getDataAll_Windows_Mac(self):
        # Read sensor data array
        data = self.device.read(102,timeout_ms = 100)
        # Most likely, the data will be 102 bytes long. if its NOT 102 bytes long, read until its 102 bytes long.
        while (len(data)) != 102:
            data = self.device.read(102,timeout_ms = 100)
            print("expecting 102 bytes but received only " + str(len(data)) + "bytes")
        # Make sure that if this part of the code is read, the data is indeed 102 bytes long
        assert len(data) == 102

        # I dont really know how these next few lines of code works, but it converts the sensor raw HID data array readings into readable format.
        hex_string = "".join(map(lambda dec: f"{dec:02x}", data))
        hex_data = re.findall("...", hex_string)
        adc_data = list(map(lambda hex: int(hex, 16), hex_data))
        
        #This array is for when the finger is pointed down, which is the proper default orientation for when the finger is mounted on a gripper.
        baseArray = np.array([[0, adc_data[31], adc_data[22], adc_data[40], adc_data[2],0],
                    [adc_data[63], adc_data[26], adc_data[24], adc_data[6], adc_data[4], adc_data[0]],
                    [adc_data[51], adc_data[27], adc_data[49], adc_data[14], adc_data[41], adc_data[13]],
                    [adc_data[16], adc_data[53], adc_data[17], adc_data[46], adc_data[42], adc_data[45]],
                    [adc_data[23], adc_data[62], adc_data[57], adc_data[38], adc_data[33], adc_data[1]],
                    [adc_data[29], adc_data[59], adc_data[19], adc_data[11], adc_data[5], adc_data[3]],
                    [adc_data[28], adc_data[20], adc_data[56], adc_data[39], adc_data[10], adc_data[35]],
                    [adc_data[21], adc_data[55], adc_data[54], adc_data[7], adc_data[8], adc_data[12]],
                    [adc_data[30], adc_data[58], adc_data[18], adc_data[47], adc_data[36], adc_data[32]],
                    [adc_data[61], adc_data[25], adc_data[48], adc_data[15], adc_data[37], adc_data[34]],
                    [adc_data[60], adc_data[52], adc_data[50], adc_data[44], adc_data[43], adc_data[9]]])
        
        # crop sensor array height and width, starting from defined x and y origin. Remember, input is (HEIGHT, WIDTH)
        croppedArray = baseArray[self.yOrigin : (self.yOrigin + self.sensorArrayHeight), self.xOrigin : (self.xOrigin + self.sensorArrayWidth)]
        #print (self.yOrigin + self.sensorArrayHeight)
        #print(croppedArray)
        return croppedArray
        
    def getAverageAll(self): # returns single averaged value of all sensors
        allTaxels = self.getDataAll().flatten() # Get all readings from cropped area of sensor and flatten into 1D array
        averageAllReading = np.sum(allTaxels)/self.sensorArrayTotalLength # get average reading of all sensors in cropped area
        return averageAllReading # Return average reading

    def getAverageActivated(self): # returns single averaged value of only activated sensors, and the number of activated taxels
        allTaxels = self.getDataAll().flatten() # Flatten all readings from cropped area of sensor into 1D array
        allTaxels[allTaxels < self.taxelThreshold] = 0  # Replace all taxels that read less than the threshold to zero
        numberOfActivatedTaxels = np.count_nonzero(allTaxels) # Find the number of taxels that read more than 0
        #numberOfActivatedTaxels, allTaxels = self.getNumberOfActivatedTaxels()
        avgActivatedReading = np.sum(allTaxels) / numberOfActivatedTaxels # Find average of all non 0 values
        return avgActivatedReading, numberOfActivatedTaxels
    
    ''' ####################################################
        Callback functions.
    #################################################### '''
    def onTaxelTrigger(): # callback function for when a taxel is triggered
        pass

    def onTouch(): # Callback function for when touch is detected
        pass
    
    def addSensorSaturationCallback(self, callback):
        self.saturationCallbacks.append(callback)

    def onSensorSaturation(self): # Callbackfunction for when sensor detects saturation in any taxel
        maxId = 0 #compute Id
        for callback in self.saturationCallbacks:
            callback(maxId)

    def __onSlipDetected(): # Callback function for when sensor detects slip
        pass

    def returnSetupValues(self):
        print("x origin: " + str(self.xOrigin))
        print("y origin: " + str(self.yOrigin))
        print("array height: " + str(self.sensorArrayHeight))
        print("array width: " + str(self.sensorArrayWidth))
        print("min number of taxels for touch: " + str(self.minNumberOfTaxelsForTouch))
        print("taxel reading threshold: " + str(self.taxelThreshold))
        print("taxel max value: " + str(self.maxValue))
        print("taxel min value: " + str(self.minValue))
        print("USB device: " + str(self.device))
        print(self.operatingSystem)
        # print("USB device serial number: " + usb.util.get_string(self.device,self.device.iSerialNumber)) # ACCESS DEVICE SERIAL NUMBER!!!