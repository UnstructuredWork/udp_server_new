import cv2
import zlib
import struct
import pickle
import numpy as np

from .server import Server
from datetime import datetime

class DeticServer(Server):
    def __init__(self, PORT):
        super().__init__(PORT)

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
                result = pickle.loads(zlib.decompress(self.all_data))

                self.server_get_img_time = datetime.now().time().isoformat()
                self.get_fps()
                self.get_mean_fps()

                self.get_latency()
                self.get_mean_latency()

                self.show()

                classes = result[0]
                bboxes = result[1]
                mask = result[2]

                # if want to show detection info
                '''
                print('Detection Results: ')
                print('=' * 70)

                for i in range(len(classes)):
                    print('Class ' + str(i+1) + ': ' + str(classes[i]))
                    print('  - Bounding Box: ' + str(bboxes[i]))
                    print()

                print('Mask:')
                print(mask)
                print('=' * 70)
                print()
                '''

                if self.VIS:
                    vmask = mask.astype(np.uint8)
                    vmask = cv2.applyColorMap(vmask, cv2.COLORMAP_JET)
                    for bbox in bboxes:
                        bbox[0::2] *= 540
                        bbox[1::2] *= 360
                        bbox = bbox.astype(int)
                        vmask = cv2.rectangle(vmask, bbox[:2], bbox[2:], (0, 0, 255), 3)

                    cv2.imshow('detic', cv2.resize(vmask, [960, 540]))
                    cv2.waitKey(1)