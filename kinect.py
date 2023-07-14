from src.server.kinect_server import KinectServer

KINECT_PORT = 5003

kinect = KinectServer(KINECT_PORT)

if __name__ == "__main__":
    kinect.run()