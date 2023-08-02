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

        self.categories = [
            {"color": [0, 0, 0],       "name": "_background_",          "id": 0},
            {"color": [100, 0, 255],   "name": "person",                "id": 1},
            {"color": [255, 150, 150], "name": "circular_valve",        "id": 2},
            {"color": [200, 255, 0],   "name": "control_box",           "id": 3},
            {"color": [255, 150, 0],   "name": "emergency_stop_switch", "id": 4},
            {"color": [255, 0, 0],     "name": "fire_extinguisher",     "id": 5},
            {"color": [255, 0, 255],   "name": "fire_extinguisher_box", "id": 6},
            {"color": [255, 255, 0],   "name": "fire_hydrant",          "id": 7},
            {"color": [0, 100, 255],   "name": "manometer",             "id": 8},
            {"color": [0, 255, 255],   "name": "safety_sign",           "id": 9},
            {"color": [0, 255, 0],     "name": "starting_switch",       "id": 10},
            {"color": [0, 0, 255],     "name": "straight_valve",        "id": 11},
            {"color": [255, 255, 255], "name": "warning_light",         "id": 12},
        ]

        self.cat_colors = []
        self.cat_names = []

        for class_info in self.categories:
            self.cat_colors.append(class_info["color"])
            self.cat_names.append(class_info["name"])

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
                ids     = result[1]
                bboxes  = result[2]
                mask    = result[3]

                if self.VIS:
                    colors = [self.cat_colors[i] for i in classes]
                    labels = [self.cat_names[i] for i in classes]

                    vmask = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)

                    for i, (cls, bbox, color) in enumerate((zip(classes, bboxes, colors))):
                        bbox[0::2] *= mask.shape[1]
                        bbox[1::2] *= mask.shape[0]
                        bbox = bbox.astype(int)

                        cv2.rectangle(vmask, bbox[:2], bbox[2:], colors[i], 3)
                        cv2.putText(vmask, labels[i], (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i])

                        if ids[0] != 0:
                            cv2.putText(vmask, str(ids[i]), (bbox[0], bbox[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i])

                        vmask[mask == cls] = color

                    cv2.imshow('detic', cv2.resize(vmask, [960, 540]))
                    cv2.waitKey(1)