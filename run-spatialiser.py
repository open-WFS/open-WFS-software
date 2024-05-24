#!/usr/bin/env python3

from spatialiser import Spatialiser
import argparse
import time

def main(args):
    print("Creating spatialiser...")
    spatialiser = Spatialiser(show_cpu=args.show_cpu)
    spatialiser.start()
    spatialiser.add_sources()

    try:
        if args.sound_check:
            spatialiser.run_sound_check()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Terminating...")
        spatialiser.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the spatialiser")
    parser.add_argument("--sound-check", action="store_true", help="Run a sound check")
    parser.add_argument("--show-cpu", action="store_true", help="Show CPU usage")
    args = parser.parse_args()
    main(args)