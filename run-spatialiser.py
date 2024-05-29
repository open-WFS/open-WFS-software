#!/usr/bin/env python3

from spatialiser import Spatialiser
import coloredlogs
import numpy as np
import argparse
import time

def main(args):
    print("Creating spatialiser...")
    spatialiser = Spatialiser(show_cpu=args.show_cpu)
    spatialiser.start()

    try:
        if args.sound_check:
            spatialiser.run_sound_check()
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
    args = parser.parse_args()

    if args.verbose:
        coloredlogs.install(level="DEBUG", format="%(asctime)s %(levelname)s %(message)s")
    else:
        coloredlogs.install(level="INFO", format="%(asctime)s %(levelname)s %(message)s")

    main(args)