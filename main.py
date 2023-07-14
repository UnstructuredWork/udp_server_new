import argparse

from src.config import get_cfg
from src.engine import Engine

def main():
    args = get_parser()
    cfg = setup_cfg(args.config_file)

    e = Engine(cfg)
    e.run()

def setup_cfg(cfg_file):
    cfg = get_cfg()
    cfg.merge_from_file(cfg_file)
    return cfg

def get_parser():
    parser = argparse.ArgumentParser(description="Cloud Server configs")
    parser.add_argument('-c', '--config-file',
                        default="./config/config.yaml",
                        help="A configuration file of camera")
    return parser.parse_args()

if __name__ == '__main__':
    main()