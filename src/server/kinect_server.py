import cv2
import struct
import pickle
import numpy as np

from .server import Server
from datetime import datetime

class KinectServer(Server):
    def __init__(self, PORT):
        super().__init__(PORT)

        self.depth = None

    def recv_udp(self):
        seg, addr = self.sock.recvfrom(self.MAX_DGRAM)
        seg = seg.split(b'end')
        if struct.unpack("B", seg[0])[0] > 1:
            self.tmp_data += seg[6]
        else:
            self.client_get_img_time = seg[3].decode('utf-8')
            self.tmp_data += seg[6]
            self.all_data = self.tmp_data
            self.tmp_data = b''

            is_data_corrupted = self.checksum(seg[1])
            if is_data_corrupted:
                print("corrupted image has been deleted")
            else:
                self.all_data = self.all_data.split(b'frame')
                self.rgb = self.decomp.decode(self.all_data[0])
                self.depth = cv2.imdecode(np.asarray(bytearray(self.all_data[1]), dtype=np.uint8),
                                          cv2.IMREAD_UNCHANGED)
                self.server_get_img_time = datetime.now().time().isoformat()
                self.get_fps()
                self.get_mean_fps()

                self.get_latency()
                self.get_mean_latency()

                self.show()

                # self.depth = cv2.applyColorMap(self.depth.astype(np.uint8), cv2.COLORMAP_JET)
                if self.VIS:
                    cv2.imshow(str(self.PORT) + '_color', self.rgb)
                    cv2.imshow(str(self.PORT) + '_depth', self.depth)

                    cv2.waitKey(1)
