import time
import random
from rodentVR.globals import *
from ursina import *

class Rule:

    state = 0 #0: outside; 1: marginal; 2: inside;
    type_ = "Rule"
    ID = f"{type_}"
    events = []
    in_duration = 0
    e = None #entity
    out = lambda _:None
    time_in_ = None

    out_add = lambda _:None
    hit_add = lambda _:None

    def __init__(self, **params):
        global RULE_INDEX
        RULE_INDEX += 1

        self.hit = self.hit_
        self.update = self.in_timer
        print(f"Rule '{self.type_}' instantiated")


    def hit_(self):
        if self.state == 0:
            self.state = 1
            print(f"entering '{self.type_}' area")
            self.out = self.out_
            self.hit = lambda:None
            self.time_in_ = LOGGER.register({"state": self.state}, self.ID)
        self.hit_add()

    def out_(self):
        if self.state != 0:
            self.state = 0
            time_out_ = LOGGER.register({"state": self.state}, self.ID)
            print(f"leaving '{self.type_}' area. duration: {time_out_ - self.time_in_} s")

        self.out = lambda:None
        self.hit = self.hit_
        self.out_add()

    def in_timer(self):
        in_duration = LOGGER.TIME - self.time_in_
        return in_duration


class Stop(Rule):

    type_ = "Stop"

    limit = 5 #default stop threshold is 5 seconds
    update_add = lambda _:None
    stim = None

    def __init__(self, **params):
        super().__init__(**params)

        try:
            self.limit = int(params["limit"])
        except KeyError:
            pass

        try:
            self.stimuli = params["stimuli"]
            self.total_stims = len(self.stimuli)
            if not "stim" in self.stimuli.keys():
                self.stim = random.choice(list(self.stimuli.values())) #medmindre params har sat
            else:
                self.stim = int(self.stim["stim"])

            if "exec" in self.stim.keys():
                for execution in list(self.stim["exec"].keys()):

                    exec(f"self.{execution}_add = lambda:exec({repr(self.stim['exec'][execution])})")

        except KeyError:
            pass

        self.update = lambda:None
        self.ID = f"{self.ID}_{self.type_}_{RULE_INDEX}" #todo: class omstrukturér


    def out_(self):
        super().out_()
        self.update = lambda:None

    def hit_(self):
        super().hit_()
        self.update = self.update_

    def update_(self):
        in_duration = super().in_timer()

        if in_duration > self.limit:

            try:
                stim_id = self.stim["id"]
            except KeyError:
                stim_id = "None"
                print("WARNING: stimulus ID not set")

            self.update_add()

            self.state = 3
            LOGGER.register({"state": self.state, "stim_id" : stim_id, "in_duration" : in_duration}, self.ID)
            self.update = lambda:None
            self.e.disable()
            print(f"Rule area '{self.type_}' disabled.")
