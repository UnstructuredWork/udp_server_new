from fvcore.common.config import CfgNode as CN


_C = CN()

_C.VERSION = 0.1
_C.CUDA = False
_C.OCL = False

_C.HOST = '127.0.0.1'
_C.GPU_DECOMPRESSION = True
_C.IMAGE_SHOW = True

_C.PORT = CN()
_C.PORT.STEREO_L = 0
_C.PORT.STEREO_R = 0
_C.PORT.RGBD = 0
_C.PORT.DETECTION = 0
_C.PORT.MONO_DEPTH = 0

_C.SW_INFO = CN()
_C.SW_INFO.STEREO_L = True
_C.SW_INFO.STEREO_R = True
_C.SW_INFO.RGBD = True
_C.SW_INFO.DETECTION = True
_C.SW_INFO.MONO_DEPTH = True