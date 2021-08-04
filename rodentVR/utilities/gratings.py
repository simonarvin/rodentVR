import numpy as np
from PIL import Image
import os
import cv2



PARENT_BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
TEXTURE_PATH = f"{PARENT_BASE_PATH}/textures/gratings/"

import sys
sys.path.append(f"{PARENT_BASE_PATH}")

from globals import *

class Grating:

    degrees = {
    "0": 0,
    "45": -1,
    "-45": 1,
    "90": 0
    }

    def __init__(self, sf = 1, angle = 0, square = False, BLOCK_HEIGHT = None, tile_size = 2**8):

        angle = str(int(angle))

        if not angle in self.degrees.keys():
            raise Exception(f"angle not supported.\nsupported angles are: {self.degrees.keys()}")

        tile_size = tile_size
        self.raw_sf = sf
        if int(sf) == sf:
            self.remainder = 0
        else:
            self.remainder = sf - int(sf)
            sf = int(sf)

        spatial_frequency = sf

        self.sf = sf

        self.angle = angle
        self.square = square

        texture_path = self.texture_ = f"{TEXTURE_PATH}grating_sf{self.raw_sf}_deg{angle}_sq{self.square}.png"
        if os.path.isfile(texture_path):
            print("texture exists")
            self.img = Image.open(texture_path)
            return

        tile_size *= 2 #due to subsequent cropping
        spatial_frequency *= 2 #due to subsequent cropping
        crop = tile_size//4

        sine_canvas = np.linspace(0, 2 * np.pi, tile_size)

        sine_canvas = 255 * (np.sin(sine_canvas * spatial_frequency) + 1)/2
        grating_canvas = np.ndarray((tile_size, tile_size), dtype=np.uint8)

        for i in range(tile_size):
            grating_canvas[i,:] = np.roll(sine_canvas, i * self.degrees[angle])

        #grating_canvas = self.rotate(grating_canvas, angle)

        grating_canvas = grating_canvas[crop:-crop, crop:-crop]

        if angle == "90":
            grating_canvas = np.rot90(grating_canvas)

        #inv_grating_canvas = np.abs(grating_canvas - 255.)
    #    print(inv_grating_canvas[0], grating_canvas[0])

        if square:
            grating_canvas[grating_canvas > 255/2] = 255
            grating_canvas[grating_canvas < 255/2] = 0


        grating_canvas = np.vstack((grating_canvas, ) * int(BLOCK_HEIGHT))

        grating_canvas = np.stack((grating_canvas,)*3, axis=-1)


        self.img = grating_canvas.astype(np.uint8)

        Image.fromarray(self.img, 'RGB').save(texture_path)


    def texture(self):
        return self.texture_

    def elongate(self, h:int): #elongates the texture to fit model uvs

        output = f"{TEXTURE_PATH}grating_sf{self.raw_sf}_deg{self.angle}_sq{self.square}_e{h}.png"
        if os.path.isfile(output):
            print("elongated texture exists")
            return output

        if self.remainder != 0:
            img = cv2.resize(np.array(self.img,dtype=np.uint8), None, fx = self.sf/(1 + self.remainder), fy=1)
        else:
            img = self.img
        elongated = np.hstack((img, ) * h)
        Image.fromarray(elongated, 'RGB').save(output)
        return output


    def rotate(self, image, angle):
        """
        src: https://stackoverflow.com/questions/9041681/opencv-python-rotate-image-by-x-degrees-around-specific-point
        """

        image=np.array(image,dtype=np.uint8)
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
        return result
