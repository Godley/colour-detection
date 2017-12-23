import cv2
import numpy as np
import logging


LOGGER = logging.getLogger(__name__)


def test(img_path):
    img = cv2.imread(img_path, 1)
    colours = ["yellow", "orange", "green", "purple", "red"]

    hues = calibrate(img, colours)
    for colour in colours:
        ball = detect(img, hues[colour][0], hues[colour][1])
        LOGGER.debug(ball)


def calibrate(image, colours):
    """
    Method to calibrate the hues and bounds based on user input

    :param image: cv2.imread image
    :param colours: list of str, colours to process

    :return: dict (str, tuple) indexed by colour, value is lower and upper bounds np arrays
    """
    blurred_image = cv2.medianBlur(image, 5)

    # Convert the image from 'BGR' to HSV colour space
    convert_image = cv2.cvtColor(blurred_image, cv2.COLOR_RGB2HSV)
    hues = {}
    lower = None
    upper = None
    for colour in colours:
        increment = 0
        hue = 0
        while True:
            up_hue = "u"
            down_hue = "d"
            up_gap = "w"
            down_gap = "s"
            complete = "y"
            LOGGER.info("Colour: %s, Controls: press %s to up the hue, \n"
                        "%s to lower the hue, \n"
                        "%s to up the range, \n"
                        "%s to lower the range, \n"
                        "%s to save",
                  colour, up_hue, down_hue, up_gap, down_gap, complete)
            lower = np.array((hue, 100, 100), dtype=np.uint8)
            upper = np.array((hue+increment, 255, 255), dtype=np.uint8)
            LOGGER.debug("hue: %i, increment: %i", hue, increment)
            imrange = cv2.inRange(convert_image, lower, upper)
            cv2.imshow('range',imrange)
            key = cv2.waitKey(0)
            if key == ord(up_hue):
                hue += 1
            if key == ord(down_hue):
                hue -= 1
            if key == ord(up_gap):
                increment += 1
            if key == ord(down_gap):
                increment -= 1
            if key == ord(complete):
                break
            cv2.destroyAllWindows()
        hues[colour] = (lower, upper)
    return hues


def detect(image, lower, upper):
    """
    Method to detect a given pair of bounds of colours within an image
    :param image: cv2.imread image
    :param lower: np array
    :param upper: np array
    :return: list, [x, y, area]
    """
    blurred_image = cv2.medianBlur(image, 5)

    # Convert the image from 'BGR' to HSV colour space
    convert_image = cv2.cvtColor(blurred_image, cv2.COLOR_RGB2HSV)

    # We want to extract the 'Hue', or colour, from the image. The 'inRange'
    # method will extract the colour we are interested in (between 0 and 180)

    imrange = cv2.inRange(convert_image, lower, upper)

    # Find the contours
    contourimage, contours, hierarchy = cv2.findContours(imrange, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Go through each contour
    found_area = -1
    found_x = -1
    found_y = -1
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cx = x + (w / 2)
        cy = y + (h / 2)
        area = w * h
        if found_area < area:
            found_area = area
            found_x = cx
            found_y = cy
    if found_area > 0:
        ball = [found_x, found_y, found_area]
    else:
        ball = None
    return ball

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test('/Users/charlottegodley/Projects/colour-detection/circles.png')