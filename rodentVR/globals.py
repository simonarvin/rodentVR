import os

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_PATH = f"{BASE_PATH}/logs/"
try:
    os.mkdir(LOG_PATH)
except:
    pass

BUFFER_SIZE = 2**12 #Logger

from logger import Logger
LOGGER = Logger()

PLAYER = []

RULE_INDEX = 0
#item pixel codes
yBOX =(200, 200, 0)

ITEM_IDENTIFIERS = [yBOX]

#env pixel codes
PLAYER_ = (255, 0 , 0)
PLAYER_DIR_ = (200, 0, 0)

BLOCK_ = (0, 0, 0)
rBLOCK_ = (100, 0, 0)
gBLOCK_ = (0, 100, 0)
bBLOCK_ = (0, 0, 100)

sineBLOCKS = 6
sineBLOCKS_ = [(n * 10 + 100,) * 3 for n in range(sineBLOCKS)]

BLOCK_IDENTIFIERS = [BLOCK_, rBLOCK_, gBLOCK_, bBLOCK_]
BLOCK_IDENTIFIERS_str = ["block"] * len(BLOCK_IDENTIFIERS)
BLOCK_IDENTIFIERS += (*sineBLOCKS_,)
BLOCK_IDENTIFIERS_str += ["grating"] * sineBLOCKS


bFLOOR = (0, 0, 50)
rFLOOR = (50, 0, 0)
gFLOOR = (0, 50, 0)
wFLOOR = (250, 250, 250)
BLOCK_IDENTIFIERS += (bFLOOR,rFLOOR, gFLOOR,wFLOOR,)
BLOCK_IDENTIFIERS_str += ["floor"] * 4

#rule pixel codes
STOP_ = (255, 0, 0)

RULE_IDENTIFIERS = [STOP_]
RULES = ["stop"]
