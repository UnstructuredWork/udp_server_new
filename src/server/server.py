from __future__ import division
import cv2
import zlib
import time
import queue
import socket
import struct

from nvjpeg import NvJpeg
from datetime import datetime
from turbojpeg import TurboJPEG
from src.load_cfg import LoadConfig

class Server:
    def __init__(self, PORT):
        self.config = LoadConfig("./config/config.yaml").info

        if self.config["GPU_DECOMPRESSION"]:
            self.decomp = NvJpeg()
        else:
            self.decomp = TurboJPEG()

        self.PORT = PORT
        self.HOST = self.config["HOST"]
        self.VIS = self.config["IMAGE_SHOW"]

        self.MAX_DGRAM = 2 ** 16

        self.sock = None
        self.sock_udp()

        self.tmp_data = b''
        self.all_data = None

        self.rgb = None

        self.client_get_img_time = None
        self.server_get_img_time = None

        self.latency = 0
        self.sum_latency = 0
        self.mean_latency = 0
        self.latency_queue = queue.Queue()

        self.sec = 0
        self.curr_time = time.time()
        self.prev_time = time.time()

        self.fps = 0
        self.sum_fps = 0
        self.mean_fps = 0
        self.fps_queue = queue.Queue()

    def __del__(self):
        self.sock.close()

    def sock_udp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.HOST, self.PORT))
        self.dump_buffer()

    def checksum(self, header):
        checksum = zlib.crc32(self.all_data)
        udp_header = struct.unpack("!I", header)
        correct_checksum = udp_header[0]

        return correct_checksum != checksum

    def dump_buffer(self):
        while True:
            seg, addr = self.sock.recvfrom(self.MAX_DGRAM)
            seg = seg.split(b'end')
            if struct.unpack("B", seg[0])[0] == 1:
                print("finish emptying buffer")
                break

    def get_fps(self):
        self.curr_time = time.time()
        self.sec = self.curr_time - self.prev_time
        self.prev_time = self.curr_time
        if self.sec > 0:
            result = round((1 / self.sec), 1)
        else:
            result = 1

        self.fps = str(result)

    def get_mean_fps(self):
        if self.fps_queue.qsize() == 100:
            self.sum_fps -= self.fps_queue.get()

        self.fps_queue.put(float(self.fps))
        self.sum_fps += float(self.fps)
        self.mean_fps = str(round(self.sum_fps / self.fps_queue.qsize(), 1))

    def get_latency(self):
        try:
            start = datetime.strptime(self.client_get_img_time, '%H:%M:%S.%f')
        except ValueError:
            start = datetime.strptime(self.client_get_img_time + '.0', '%H:%M:%S.%f')
        try:
            end = datetime.strptime(self.server_get_img_time, '%H:%M:%S.%f')
        except ValueError:
            end = datetime.strptime(self.server_get_img_time + '.0', '%H:%M:%S.%f')

        result = round((end - start).total_seconds() * 1000, 1)

        self.latency = str(result)

    def get_mean_latency(self):
        if self.latency_queue.qsize() == 100:
            self.sum_latency -= self.latency_queue.get()

        self.latency_queue.put(float(self.latency))
        self.sum_latency += float(self.latency)
        self.mean_latency = str(round(self.sum_latency / self.latency_queue.qsize(), 1))

    def show(self):
        print('-' * 15 + ' ' * 3 + str(self.PORT) + ' ' * 3 + '-' * 15)
        print('Latency:                        ' + self.latency)
        print('MeanLatency:                    ' + self.mean_latency)
        print('FPS:                            ' + self.fps)
        print('MeanFPS:                        ' + self.mean_fps)
        print('-' * 40)

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
                self.rgb = self.decomp.decode(self.all_data)

                self.server_get_img_time = datetime.now().time().isoformat()
                self.get_fps()
                self.get_mean_fps()

                self.get_latency()
                self.get_mean_latency()

                self.show()

                if self.VIS:
                    cv2.imshow(str(self.PORT), self.rgb)
                    cv2.waitKey(1)

    def run(self):
        while True:
            self.recv_udp()