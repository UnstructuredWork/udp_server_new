from threading import Thread
from src.server.server import Server

LEFT_PORT = 5001
RIGHT_PORT = 5002

left = Server(LEFT_PORT)
right = Server(RIGHT_PORT)

l_thr = Thread(target=left.run, args=())
r_thr = Thread(target=right.run, args=())

if __name__ == "__main__":
    l_thr.start()
    r_thr.start()
