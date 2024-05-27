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
            input_buffer = spatialiser.input_channels.output_buffer[0]
            input_buffer_rms = np.sqrt(np.mean(np.square(input_buffer)))
            input_buffer_rms_db = 20.0 * np.log10(input_buffer_rms)
            print("Input RMS: %.2fdB" % input_buffer_rms_db)
            print("%f, %f" % (input_buffer[0], input_buffer[1]))
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
        coloredlogs.install(level="DEBUG")
    else:
        coloredlogs.install(level="INFO")

    main(args)