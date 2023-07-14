from src.server.depth_server import DepthServer

DEPTH_PORT = 5052

depth = DepthServer(DEPTH_PORT)

if __name__ == "__main__":
    depth.run()