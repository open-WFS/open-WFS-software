#!/usr/bin/env python3

from spatialiser.constants import osc_port
import pythonosc.udp_client
import coloredlogs
import argparse
import logging
import random
import time

logger = logging.getLogger(__file__)

def main(args):
    logger.info("Creating OSC client...")
    osc_client = pythonosc.udp_client.SimpleUDPClient("127.0.0.1", osc_port)
    while True:
        osc_client.send_message("/source/1/xyz", [
            random.uniform(-1, 1),
            random.uniform(-1, 1),
            random.uniform(0, 1)
            ])
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the spatialiser")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.verbose:
        coloredlogs.install(level="DEBUG", fmt="%(asctime)s [%(levelname)s] %(message)s")
    else:
        coloredlogs.install(level="INFO", fmt="%(asctime)s [%(levelname)s] %(message)s")

    main(args)