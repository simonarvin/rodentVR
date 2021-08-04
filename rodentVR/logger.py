import time
import numpy as np
import os
from constants import *

class Logger:
    TIME = None
    START = None

    buffer = np.zeros(BUFFER_SIZE + 1, dtype=dict)
    index = 0
    pack = 0
    TIMESTAMP = time.strftime('%m%d%y_%H%M%S')


    def __init__(self):
        
        #mkdir timestamp, add experiment information
        self.DIR = f"{LOG_PATH}/{self.TIMESTAMP}"
        try:
            os.mkdir(self.DIR)
        except OSError:
            pass #folder already exists

        self.save = lambda:None #REMOVE


    def start(self):
        self.START = time.time()

    def update(self, coords):
        self.TIME = time.time()
        self.buffer[self.index] = {"xyz" : (*coords,)}
        self.increment()


    def clear(self):
        index = 0
        #todo: if buffer empty, save it
        buffer = np.zeros(BUFFER_SIZE, dtype=dict)

    def save(self):
        try:
            np.save(f"{self.DIR}/pack{self.pack}",self.buffer)
            self.pack += 1
            print("log saved")
        except Exception as e:
            raise e("FAILED: log could not be saved. Printed to runtime-log instead")
            #todo: kan printes i log.logger


    def terminate(self):
        self.buffer = self.buffer[:self.index] #crop to used buffer-size
        self.save()
        print("log terminated")

    def increment(self):
        if self.index == BUFFER_SIZE:
            self.index = 0
            self.save()
        else:
            self.index += 1

    def register(self, dict_, parent_id = None):
        self.buffer[self.index] = {**dict_, **{"ID" : parent_id}}
        self.increment()
        return self.TIME


        #self.events.append({"time" : self.TIME, event : value})
