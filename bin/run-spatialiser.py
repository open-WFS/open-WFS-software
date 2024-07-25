#!/usr/bin/env python3

from spatialiser import Spatialiser
import coloredlogs
import argparse
import time

import logging
logger = logging.getLogger(__file__)

def main(args):
    logger.info("Creating spatialiser...")
    spatialiser = Spatialiser(show_cpu=args.show_cpu)

    try:
        if args.sound_check:
            spatialiser.run_sound_check()
        elif args.dump_spat_layout:
            spatialiser.dump_spat_layout()
        else:
            spatialiser.start()
            while True:
                spatialiser.tick()
                time.sleep(2)
    except KeyboardInterrupt:
        print("Terminating...")
        spatialiser.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the spatialiser")
    parser.add_argument("--sound-check", action="store_true", help="Run a sound check")
    parser.add_argument("--show-cpu", action="store_true", help="Show CPU usage")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--dump-spat-layout", action="store_true", help="Print speaker layout suitable for Max/MSP Spat config")
    args = parser.parse_args()

    if args.verbose:
        coloredlogs.install(level="DEBUG", fmt="%(asctime)s [%(levelname)s] %(message)s")
    else:
        coloredlogs.install(level="INFO", fmt="%(asctime)s [%(levelname)s] %(message)s")

    main(args)
