#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# OpenWFS: Example spatialiser client.
#
# This script connects to the spatialiser process (running in Spat or Python)
# and sends OSC messages to continually set the position of a sound source.
# 
# Positioning messages are of the format:
#
#    /source/<index>/xyz <x> <y> <z>
#
# where <index> is the number of the sound source (beginning from 1), and
# <x>, <y> and <z> are the floating-point coordinates, typically in metres.
#--------------------------------------------------------------------------------

from spatialiser.constants import osc_port
import pythonosc.udp_client
import coloredlogs
import argparse
import logging
import math
import time

logger = logging.getLogger(__file__)

def main(args):
    logger.info("Creating OSC client...")
    osc_client = pythonosc.udp_client.SimpleUDPClient("127.0.0.1", args.osc_port)

    x_lfo_amplitude = 1.0
    x_lfo_frequency = 0.2
    interval = 0.01
    frame_count = 0

    while True:
        # Oscillate the sound source from left to right.
        x_pos = x_lfo_amplitude * math.sin(x_lfo_frequency * math.pi * 2 * frame_count * interval)
        osc_client.send_message("/source/1/xyz", [x_pos, 3, 0])
        frame_count += 1
        time.sleep(interval)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the spatialiser")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--osc-port", type=int, default=osc_port)
    args = parser.parse_args()

    if args.verbose:
        coloredlogs.install(level="DEBUG", fmt="%(asctime)s [%(levelname)s] %(message)s")
    else:
        coloredlogs.install(level="INFO", fmt="%(asctime)s [%(levelname)s] %(message)s")

    main(args)
