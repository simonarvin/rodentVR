from panda3d.core import Filename
import os
import numpy as np
import cv2
from ursina import *

class Capture:
    def __init__(self, LEVEL_PATH):
        self.SNAPSHOT_PATH = f"{LEVEL_PATH}snapshots/"
        try:
            os.mkdir(self.SNAPSHOT_PATH)
        except OSError:
            pass #folder already exists

    def snapshot(self):
        file_path = f"{self.SNAPSHOT_PATH}kk.png".replace("\\", "/")
        base.screenshot()
        base.graphicsEngine.renderFrame()

        dr = base.camNode.getDisplayRegion(0)
        tex = dr.getScreenshot()
        data = tex.getRamImage()
        v = memoryview(data).tolist()
        img = np.array(v,dtype=np.uint8)
        img = img.reshape((tex.getYSize(),tex.getXSize(),4))
        img = img[::-1]
        cv2.imwrite(file_path, img)
        print("SAVED")
