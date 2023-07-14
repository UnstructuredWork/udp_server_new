from src.server import *
from src.parallel import thread_method

class Engine:
    def __init__(self, cfg):
        self.cfg = cfg.clone()

    @thread_method
    def execute(self, obj, port):
        s = obj(port)
        s.run()

    def run(self):
        if self.cfg.SW_INFO.STEREO_L:
            self.execute(Server, self.cfg.PORT.STEREO_L)

        if self.cfg.SW_INFO.STEREO_R:
            self.execute(Server, self.cfg.PORT.STEREO_R)

        if self.cfg.SW_INFO.RGBD:
            self.execute(KinectServer, self.cfg.PORT.RGBD)

        if self.cfg.SW_INFO.DETECTION:
            self.execute(DeticServer, self.cfg.PORT.DETECTION)

        if self.cfg.SW_INFO.MONO_DEPTH:
            self.execute(DepthServer, self.cfg.PORT.MONO_DEPTH)