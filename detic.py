from src.server.detic_server import DeticServer

DETIC_PORT = 5050

detic = DeticServer(DETIC_PORT)

if __name__ == "__main__":
    detic.run()