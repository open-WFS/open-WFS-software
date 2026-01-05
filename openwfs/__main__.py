import sys
from .spatialiser import Spatialiser
from loguru import logger

import argparse

def main(config_path: str,
         room_path: str,
         show_status: bool,
         sound_check: bool = False,
         gain: float = 0.0):
    spatialiser = Spatialiser(config_path,
                              room_path,
                              show_status=show_status,
                              gain=gain)
    spatialiser.start()

    if sound_check:
        spatialiser.run_sound_check()
    
    try:
        spatialiser.graph.wait()
    except KeyboardInterrupt:
        print("\nTerminating...")
        spatialiser.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenWFS Python Panner")
    parser.add_argument("--config", "-c", default="default", help="Path to config file")
    parser.add_argument("--room", "-r", default="studio-2025-v2a", help="Path to room file")
    parser.add_argument("--show-status", action="store_true", help="Show audio graph status")
    parser.add_argument("--sound-check", action="store_true", help="Run sound check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--gain", type=float, default=-12.0, help="Set gain in dB")
    args = parser.parse_args()

    logger.remove()
    logger.add(sys.stderr, format="<white>{time}</white> <yellow>{level}</yellow> {message}", level="DEBUG" if args.verbose else "INFO")

    main(config_path=args.config,
         room_path=args.room,
         show_status=args.show_status,
         sound_check=args.sound_check,
         gain=args.gain)