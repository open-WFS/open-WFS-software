#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# OpenWFS: generate-spat-layout.py
# 
# Generate coordinates for every driver of an OpenWFS module array, for use
# in the Max/MSP Spat spatialiser.
# 
# Configuration should be done by modifying the contents of
# spatialiser/constants.py, updating the `module_layout` lines with the
# centroid positions of each of the OpenWFS modules.
#--------------------------------------------------------------------------------


from openwfs import Spatialiser
import coloredlogs
import argparse
import numpy as np

import logging
logger = logging.getLogger(__file__)

def main(args):
    spatialiser = Spatialiser()
    with open(args.output_file, "w") as fd:
        layout = spatialiser.dump_spat_layout()
        fd.write(layout + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate coefficients for Spat")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("output_file", help="Path to Spat's speaker-layout.txt file")
    args = parser.parse_args()

    coloredlogs.install(level="WARNING", fmt="%(asctime)s [%(levelname)s] %(message)s")

    main(args)
