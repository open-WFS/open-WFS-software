from .spatialiser import Spatialiser

import argparse
import time

def main(config_path: str,
         room_path: str,
         show_status: bool,
         sound_check: bool = False):
    spatialiser = Spatialiser(config_path,
                              room_path,
                              show_status=show_status)
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
    parser.add_argument("--room", "-r", default="compton-martin-hackathon-2025", help="Path to room file")
    parser.add_argument("--show-status", action="store_true", help="Show audio graph status")
    parser.add_argument("--sound-check", action="store_true", help="Run sound check")
    args = parser.parse_args()

    main(config_path=args.config,
         room_path=args.room,
         show_status=args.show_status,
         sound_check=args.sound_check)