#!/usr/bin/env python
# coding: Latin

# Load library functions we want
import time
import os
import sys
# import ThunderBorg
import io
import threading
import picamera
import picamera.array
import cv2
import numpy

print('Libraries loaded')

# Global values
global running
# global TB
global camera
global processor
global debug
global colour

running = True
debug = True
colour = 'blue'

# Setup the ThunderBorg
# TB = ThunderBorg.ThunderBorg()
# TB.i2cAddress = 0x15                  # Uncomment and change the value if you have changed the board address
# TB.Init()
##if not TB.foundChip:
##    boards = ThunderBorg.ScanForThunderBorg()
##    if len(boards) == 0:
##        print('No ThunderBorg found, check you are attached :)'
##    else:
##        print('No ThunderBorg at address %02X, but we did find boards:' % (TB.i2cAddress)
##        for board in boards:
##            print('    %02X (%d)' % (board, board)
##        print('If you need to change the IÃÂ²C address change the setup line so it is correct, e.g.'
##        print('TB.i2cAddress = 0x%02X' % (boards[0])
##    sys.exit()
##TB.SetCommsFailsafe(False)

# Power settings
##voltageIn = 12.0                        # Total battery voltage to the ThunderBorg
##voltageOut = 12.0 * 0.95                # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power

# Camera settings
imageWidth = 320  # Camera image width
imageHeight = 240  # Camera image height
frameRate = 3  # Camera image capture frame rate

# Auto drive settings
autoMaxPower = 1.0  # Maximum output in automatic mode
autoMinPower = 0.2  # Minimum output in automatic mode
autoMinArea = 10  # Smallest target to move towards
autoMaxArea = 10000  # Largest target to move towards
autoFullSpeedArea = 300  # Target size at which we use the maximum allowed output

# Setup the power limits
##if voltageOut > voltageIn:
##    maxPower = 1.0
##else:
##    maxPower = voltageOut / float(voltageIn)
##autoMaxPower *= maxPower

# Image stream processing thread
class StreamProcessor(threading.Thread):
    def __init__(self):
        super(StreamProcessor, self).__init__()
        self.stream = picamera.array.PiRGBArray(camera)
        self.event = threading.Event()
        self.terminated = False
        self.start()
        self.begin = 0

    def run(self):
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    # Read the image and do some processing on it
                    self.stream.seek(0)
                    self.ProcessImage(self.stream.array, colour)
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()

    # Image processing function
    def ProcessImage(self, image, colour):
        # View the original image seen by the camera.
        if debug:
            cv2.imshow('original', image)
            cv2.waitKey(0)

        # Blur the image
        image = cv2.medianBlur(image, 5)
        if debug:
            cv2.imshow('blur', image)
            cv2.waitKey(0)

        # Convert the image from 'BGR' to HSV colour space
        image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        if debug:
            cv2.imshow('cvtColour', image)
            cv2.waitKey(0)

        # We want to extract the 'Hue', or colour, from the image. The 'inRange'
        # method will extract the colour we are interested in (between 0 and 180)
        # In testing, the Hue value for red is between 95 and 125
        # Green is between 50 and 75
        # Blue is between 20 and 35
        # Yellow is... to be found!
        if colour == "red":
            imrange = cv2.inRange(image, numpy.array((95, 127, 64)), numpy.array((125, 255, 255)))
        elif colour == "green":
            imrange = cv2.inRange(image, numpy.array((50, 127, 64)), numpy.array((75, 255, 255)))
        elif colour == 'blue':
            imrange = cv2.inRange(image, numpy.array((20, 64, 64)), numpy.array((35, 255, 255)))

        # I used the following code to find the approximate 'hue' of the ball in
        # front of the camera
        #        for crange in range(0,170,10):
        #            imrange = cv2.inRange(image, numpy.array((crange, 64, 64)), numpy.array((crange+10, 255, 255)))
        #            print(crange)
        #            cv2.imshow('range',imrange)
        #            cv2.waitKey(0)

        # View the filtered image found by 'imrange'
        if debug:
            cv2.imshow('imrange', imrange)
            cv2.waitKey(0)

        # Find the contours
        contourimage, contours, hierarchy = cv2.findContours(imrange, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if debug:
            cv2.imshow('contour', contourimage)
            cv2.waitKey(0)

        # Go through each contour
        foundArea = -1
        foundX = -1
        foundY = -1
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cx = x + (w / 2)
            cy = y + (h / 2)
            area = w * h
            if foundArea < area:
                foundArea = area
                foundX = cx
                foundY = cy
        if foundArea > 0:
            ball = [foundX, foundY, foundArea]
        else:
            ball = None
        # Set drives or report ball status
        self.SetSpeedFromBall(ball)

    # Set the motor speed from the ball position
    def SetSpeedFromBall(self, ball):
        global TB
        driveLeft = 0.0
        driveRight = 0.0
        if ball:
            x = ball[0]
            area = ball[2]
            if area < autoMinArea:
                print('Too small / far')
            elif area > autoMaxArea:
                print('Close enough')
            else:
                if area < autoFullSpeedArea:
                    speed = 1.0
                else:
                    speed = 1.0 / (area / autoFullSpeedArea)
                speed *= autoMaxPower - autoMinPower
                speed += autoMinPower
                direction = (x - imageCentreX) / imageCentreX
                if direction < 0.0:
                    # Turn right
                    print('Turn Right')
                    driveLeft = speed
                    driveRight = speed * (1.0 + direction)
                else:
                    # Turn left
                    print('Turn Left')
                    driveLeft = speed * (1.0 - direction)
                    driveRight = speed
                print('%.2f, %.2f' % (driveLeft, driveRight))
        else:
            print('No ball')


# TB.SetMotor1(driveLeft)
#        TB.SetMotor2(driveRight)

# Image capture thread
class ImageCapture(threading.Thread):
    def __init__(self):
        super(ImageCapture, self).__init__()
        self.start()

    def run(self):
        global camera
        global processor
        print('Start the stream using the video port')
        camera.capture_sequence(self.TriggerStream(), format='bgr', use_video_port=True)
        print('Terminating camera processing...')
        processor.terminated = True
        processor.join()
        print('Processing terminated.')

    # Stream delegation loop
    def TriggerStream(self):
        global running
        while running:
            if processor.event.is_set():
                time.sleep(0.01)
            else:
                yield processor.stream
                processor.event.set()


# Startup sequence
print('Setup camera')
camera = picamera.PiCamera()
camera.resolution = (imageWidth, imageHeight)
camera.framerate = frameRate
imageCentreX = imageWidth / 2.0
imageCentreY = imageHeight / 2.0

print('Setup the stream processing thread')
processor = StreamProcessor()

print('Wait ...')
time.sleep(2)
captureThread = ImageCapture()

try:
    print('Press CTRL+C to quit')
    ##    TB.MotorsOff()
    ##    TB.SetLedShowBattery(True)
    # Loop indefinitely until we are no longer running
    while running:
        # Wait for the interval period
        # You could have the code do other work in here 🙂
        time.sleep(1.0)
        # Disable all drives
##    TB.MotorsOff()
except KeyboardInterrupt:
    # CTRL+C exit, disable all drives
    print('\nUser shutdown')
##    TB.MotorsOff()
except:
    # Unexpected error, shut down!
    e = sys.exc_info()[0]
    print
    print(e)
    print('\nUnexpected error, shutting down!')
##    TB.MotorsOff()
# Tell each thread to stop, and wait for them to end
running = False
captureThread.join()
processor.terminated = True
processor.join()
del camera
##TB.MotorsOff()
##TB.SetLedShowBattery(False)
##TB.SetLeds(0,0,0)
print('Program terminated.')