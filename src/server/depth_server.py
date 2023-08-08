import cv2
import struct
import numpy as np

from .server import Server
from datetime import datetime

class DepthServer(Server):
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
                self.depth = cv2.imdecode(np.asarray(bytearray(self.all_data), dtype=np.uint8),
                                          cv2.IMREAD_UNCHANGED)

                self.server_get_img_time = datetime.now().time().isoformat()
                self.get_fps()
                self.get_mean_fps()

                self.get_latency()
                self.get_mean_latency()

                self.show()

                if self.VIS:
                    cv2.imshow(str(self.PORT), self.depth)
                    cv2.waitKey(1)
