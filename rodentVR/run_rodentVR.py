from ursina import *
from ursina.shaders import lit_with_shadows_shader as shader_

import os
from PIL import Image

import numpy as np

import cv2
import json
#from constants import * #initialized by __init__.py

from rodentVR.globals import *
from rodentVR.rules.rules import *
from rodentVR.utilities import Grating, Capture, rectangles
from pathlib import Path

DEBUG = True

SCREENSHOT = True

class VR:

    LEVEL_LAYERS = []
    RULE_LAYERS = []
    RULE_ENTITIES = []

    SCREEN_DIMENSIONS = (1920 * 2, 1080)
    LEVEL_LAYER = 0

    LEVEL_SIZE = (-1)
    GROUND_SIZE = 1

    CAPTURE = None

    def load_parameters(self, file = "default"):
        print(f"loading parameters '{file}'")

        with open(f"{BASE_PATH}/parameters/{file}.json", "r") as f:
            params = json.loads(f.read())

        with open(f"{BASE_PATH}/parameters/default.json", "r") as f:
            #print(f.read())
            default_params = json.loads(f.read())
        try:
            base_params = {**default_params["base"], **params["base"]} #fill remaining default params
        except KeyError:
            base_params = default_params["base"]

        default_grating = default_params["default_grating"]

        try:
            self.rule_params = params["rules"]
        except KeyError:
            self.rule_params = {}



        for (key, value) in base_params.items():
            if not isinstance(value, str):
                exec(f"self.{key} = {value}")
            else:
                exec(f"self.{key} = '{value}'")

        self.LEVEL_PATH = f"{BASE_PATH}/levels/{self.LEVEL_ID}/"
        self.TEXTURE_PATH = f"{BASE_PATH}/textures/"
        print("hej", self.TEXTURE_PATH)
        self.CAPTURE = Capture(self.LEVEL_PATH)

        self.BLOCK_SIZE = (self.SCALAR, self.SCALAR * self.BLOCK_HEIGHT, self.SCALAR)
        self.ITEM_SIZE = (self.SCALAR * .5, self.SCALAR * .5, self.SCALAR * .5)
        self.RULE_SIZE = (self.SCALAR, self.SCALAR, self.SCALAR)
        self.FLOOR_SIZE = (self.SCALAR, self.SCALAR * .5, self.SCALAR)

        self.DEFAULT_GRATING = Grating(**default_grating, BLOCK_HEIGHT = self.BLOCK_HEIGHT)

        #now, check for custom blocks
        self.GRATINGS = []

        try:
            block_params = params["blocks"]
            for (key, value) in block_params.items():
                if value["type"] == "sine":
                    value = {**default_grating, **value}

                    self.GRATINGS.append(Grating(sf = value["sf"], angle = value["angle"], square = value["square"], BLOCK_HEIGHT = self.BLOCK_HEIGHT))
        except KeyError:
            block_params = None
            pass #no custom blocks added

    def load_level(self):
        print(f"loading level '{self.LEVEL_ID}'")
        for layer in range(self.MAX_LEVEL_LAYER):
            try:
                level_layer = Image.open(f"{self.LEVEL_PATH}/{layer}.{self.LEVEL_EXT}")
                level_layer = np.array(level_layer)[:,:,:3] #discarding potential alpha channel
                self.LEVEL_LAYERS.append(level_layer)
                self.LEVEL_LAYER += 1

                try:
                    rule_layer = Image.open(f"{self.LEVEL_PATH}/{layer}r.{self.LEVEL_EXT}")
                    rule_layer = np.array(rule_layer)[:,:,:3] #discarding potential alpha channel
                    self.RULE_LAYERS.append(rule_layer)
                except FileNotFoundError:
                    pass

            except FileNotFoundError:
                if self.LEVEL_LAYER == 0:
                    raise FileNotFoundError(f"FAILED: level '{self.LEVEL_ID}' was not found.")
                    return 0
                break

        self.LEVEL_SIZE = level_layer.shape
        print(f"level '{self.LEVEL_ID}' loaded. registered layer: {self.LEVEL_LAYER}")

        return 1

    def generate_level(self):
        global PLAYER
        #generate floor

        ground_parent = Entity(
        model=Mesh(vertices=[], uvs=[]),
        color = color.gray,
        texture = load_texture(name="grass.png", path=Path(self.TEXTURE_PATH))
        )
        cube = load_model('cube')

        for i in range(int(self.SCALAR * self.LEVEL_SIZE[0]/self.GROUND_SIZE) + 2):
            for j in range(int(self.SCALAR * self.LEVEL_SIZE[1]/self.GROUND_SIZE) + 2):
                ground_parent.model.vertices += [Vec3(*e) + Vec3(j * self.GROUND_SIZE, 0,  i * self.GROUND_SIZE) for e in cube.vertices] # copy the quad model, but offset it with Vec3(x+.5,y+.5,0)
                ground_parent.model.uvs += cube.uvs

        #ground_parent.texture.filtering = None
        ground_parent.model.generate()


        for level_layer_index, layer in enumerate(self.LEVEL_LAYERS):
            for index, identifier in enumerate(BLOCK_IDENTIFIERS):
                #blocks = np.where(np.all(layer == identifier, axis=-1))
                blocks_ = np.all(layer == identifier, axis=-1)
                block_type = BLOCK_IDENTIFIERS_str[index]

                rects = rectangles.extract_rectangles(blocks_.astype(int))
                for rect in rects:
                    (y, x, h, w) = rect#cv2.boundingRect(contour)

                    if "floor" == block_type:
                        e = Entity(model='cube',  scale = (self.FLOOR_SIZE[0] * w, self.FLOOR_SIZE[1], self.FLOOR_SIZE[2] * h), color=rgb(*identifier), position = (self.SCALAR * (x + w/2 - 1/2), self.SCALAR * level_layer_index * self.BLOCK_HEIGHT+ self.GROUND_SIZE/2 + self.FLOOR_SIZE[1]/2, self.SCALAR * (y + h/2 - 1/2)), collider = 'box',shader=shader_)
                    elif "block" == block_type:
                        e = Entity(model='cube',  scale = (self.BLOCK_SIZE[0] * w, self.BLOCK_SIZE[1], self.BLOCK_SIZE[2] * h), color=rgb(*identifier), position = (self.SCALAR * (x + w/2 - 1/2), self.SCALAR * level_layer_index * self.BLOCK_HEIGHT+ self.GROUND_SIZE/2+ self.BLOCK_HEIGHT/2, self.SCALAR * (y + h/2 - 1/2)), collider = 'box',shader=shader_)
                    elif "grating" == block_type:
                        try:
                            grating = self.GRATINGS[(identifier[0] - 100)//10].elongate(max(h, w))
                        except IndexError:
                            grating = self.DEFAULT_GRATING.elongate(max(h, w))

                        texture = load_texture(name = grating[0], path = Path(grating[1]))
                        e = Entity(model='cube',  scale = (self.BLOCK_SIZE[0] * w, self.BLOCK_SIZE[1], self.BLOCK_SIZE[2] * h), color=color.white, texture = texture, position = (self.SCALAR * (x + w/2 - 1/2), self.SCALAR * level_layer_index * self.BLOCK_HEIGHT+ self.GROUND_SIZE/2+ self.BLOCK_HEIGHT/2, self.SCALAR * (y + h/2 - 1/2)), collider = 'box',shader=shader_)


            if len(PLAYER) == 0:
                player = np.where(np.all(layer == PLAYER_, axis=-1))
                if len(player[0]) > 0:

                    PLAYER.append(camera)
                    PLAYER[0].dx = PLAYER[0].dz = 0.
                    PLAYER[0].position = (self.SCALAR * player[1], self.PLAYER_ELEVATION + self.SCALAR * level_layer_index * self.BLOCK_HEIGHT + self.GROUND_SIZE/2, self.SCALAR * player[0])
                    PLAYER[0].collider = BoxCollider(PLAYER[0], center=Vec3(0, 0, .1), size=Vec3(.4, .1, .1))
                    player_dir = np.where(np.all(layer == PLAYER_DIR_, axis=-1))

                    if len(player_dir[0]) > 0:
                        angle = np.degrees(-np.arctan2(player[0] - player_dir[0], player[1] - player_dir[1])) - 90
                        PLAYER[0].rotation = Vec3(0, np.abs(angle), 0)


        for item_layer_index, layer in enumerate(self.LEVEL_LAYERS):
            for index, identifier in enumerate(ITEM_IDENTIFIERS):
                items = np.where(np.all(layer == identifier, axis=-1))

                for item_index in range(items[0].shape[0]):
                    texture = load_texture(name="cheese.jpg", path=Path(self.TEXTURE_PATH))
                    e = Entity(model=Cube(), scale = self.ITEM_SIZE,texture=texture, position = (self.SCALAR *  items[1][item_index], self.SCALAR * item_layer_index * self.BLOCK_HEIGHT + self.GROUND_SIZE/2 + self.ITEM_SIZE[1]/2, self.SCALAR * items[0][item_index]), collider = 'box', shader=shader_)


        for rule_layer_index, layer in enumerate(self.RULE_LAYERS):
            for index, identifier in enumerate(RULE_IDENTIFIERS):
                #rules = np.where(np.all(layer == identifier, axis=-1))
                rules_ = np.all(layer == identifier, axis=-1).astype(np.uint8)
                #rects = rectangles.extract_rectangles(rules_.astype(int))
                contours, _ = cv2.findContours(rules_, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                contours=sorted(contours, key=lambda x:cv2.boundingRect(x)[0])
                for ci, contour in enumerate(contours):
                    (x, y, w, h) = cv2.boundingRect(contour)

                    e = Entity(model='cube', name = RULES[index], visible=False, scale = (self.RULE_SIZE[0] * w, self.RULE_SIZE[1], self.RULE_SIZE[2] * h), position = (self.SCALAR * (x + w/2 - 1/2), self.SCALAR * rule_layer_index + self.GROUND_SIZE/2 + self.RULE_SIZE[1]/2, self.SCALAR * (y + h/2 - 1/2)), collider = 'box')
                    try:
                        params = self.rule_params[str(ci)]
                    except KeyError:
                        params = {}

                    e.rule_ = eval(f"{RULES[index].title()}(**{params})") # set rule class
                    e.name = e.rule_.ID
                    e.rule_.e = e

                    self.RULE_ENTITIES.append(e)

        self.RULE_ENTITIES = tuple(self.RULE_ENTITIES)

        if SCREENSHOT:
            #self.CAPTURE.camera = camera
            saved_camera = camera.transform
            #tan(FOV/2) * 2/h = dist
            max_dim = max(self.LEVEL_SIZE)
            if max_dim == self.LEVEL_SIZE[1]:
                rotate = 0
            else:
                rotate = 90

            camera.enabled=False
            camera.orthographic = True
            delay=1
            invoke(Func(self.CAPTURE.snapshot), delay = delay) #left

            invoke(setattr,camera,'rotation',Vec3(0,90,0),delay=3*delay)
            #camera.rotation = Vec3(0,90,0)
            invoke(Func(self.CAPTURE.snapshot), delay = 4*delay) #right

            invoke(setattr,camera,'rotation',Vec3(90,0,0),delay=5*delay)
            invoke(setattr,camera,'y',100, delay=5*delay)
            invoke(Func(self.CAPTURE.snapshot), delay = 6*delay) #top-down

            invoke(setattr,camera,'enabled',True, delay=7*delay)
            invoke(setattr,camera,'orthographic',False, delay=7*delay)
            invoke(setattr,camera,'transform',saved_camera, delay=7*delay)
            #camera.transform = Vec3(self.SCALAR * self.LEVEL_SIZE[1]//2, self.LEVEL_LAYER * self.BLOCK_HEIGHT * self.SCALAR + 1/(np.tan(np.radians(self.FOV/2)) * 2/(max_dim * self.SCALAR)), self.SCALAR * self.LEVEL_SIZE[0]//2 + 1), Vec3(90,rotate,0), Vec3(1,1,1)
            #Wait(.2)
            #invoke(Func(self.CAPTURE.snapshot), delay = 1)
            #camera.transform = Vec3(self.SCALAR * self.LEVEL_SIZE[1]//2 + 1/(np.tan(np.radians(self.FOV/2)) * 2/(max_dim * self.SCALAR)), (self.LEVEL_LAYER * self.BLOCK_HEIGHT * self.SCALAR)/2, self.SCALAR * self.LEVEL_SIZE[0]//2 + 1), Vec3(0,0,-180), Vec3(1,1,1)

            #camera.enabled = True

        LOGGER.start() #start logging

    def run(self):
        app = Ursina()
        app.development_mode = DEBUG
        window.fps_counter.enabled = DEBUG
        window.exit_button.visible = DEBUG
        window.borderless = DEBUG
        window.cog_button.enabled = DEBUG

        if not DEBUG:

            window.windowed_size =window.size = self.SCREEN_DIMENSIONS
            window.position = Vec2(
                int(-1920),
                int(0)
                )

        camera.update=self.update
        camera.fov = self.FOV
        camera.orthographic = False
        mouse.locked = True
        window.color = rgb(97,94,137)

        self.generate_level()
        app.run()

    def update(self):
        LOGGER.update(camera.position)

        #print(np.cos(np.radians(-PLAYER[0].rotation[1]-90)), np.sin(np.radians(-PLAYER[0].rotation[1] +90)))
        #if PLAYER[0].rotation[1] != 90:
        PLAYER[0].z += PLAYER[0].dz
        PLAYER[0].x += PLAYER[0].dx
        #else:
        #    PLAYER[0].z -= PLAYER[0].dx
        #    PLAYER[0].x += PLAYER[0].dz


        if not self.collision_handling():
            PLAYER[0].dz += np.cos(np.radians(PLAYER[0].rotation[1])) * mouse.velocity[1] * self.VELOCITY_SCALAR - np.sin(np.radians(PLAYER[0].rotation[1])) * mouse.velocity[0] * self.VELOCITY_SCALAR
            PLAYER[0].dx += np.cos(np.radians(PLAYER[0].rotation[1])) * mouse.velocity[0] * self.VELOCITY_SCALAR + np.sin(np.radians(PLAYER[0].rotation[1])) * mouse.velocity[1] * self.VELOCITY_SCALAR

        PLAYER[0].dz *= self.FRICTION
        PLAYER[0].dx *= self.FRICTION



    def collision_handling(self):

        rule = None

        for rule in self.RULE_ENTITIES:
            if rule.enabled:
                rule_collision = PLAYER[0].intersects(rule)
                if rule_collision.hit:
                    rule.rule_.hit()
                else:
                    rule.rule_.out()
                rule.rule_.update()

        angle = np.arctan2(PLAYER[0].dz, PLAYER[0].dx)
        hit = False

        while PLAYER[0].intersects(ignore = self.RULE_ENTITIES).hit: #collision handling
            hit = True
            #rot = np.radians(PLAYER[0].rotation[1]) #todo: incorporate into ursina via super()
            PLAYER[0].x -= np.cos(angle) * .01
            PLAYER[0].z -= np.sin(angle) * .01

        return hit

def main():
    vr = VR()
    vr.load_parameters("example_1")
    vr.load_level()

    vr.run()
    LOGGER.terminate()

if __name__ == "__main__":
    main()
