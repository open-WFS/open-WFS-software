#!/usr/bin/env python3

import yaml
import argparse
import pandas as pd


def main(input_file, output_file=None, name="openwfs-v2a", panel_width=250, panel_height=250, panel_depth=100):
    input_data = pd.read_csv(input_file)

    drivers = dict()
    for n in range(len(input_data)):
        drivers[n] = {
            "position": [float(input_data["x"][n]), float(input_data["y"][n])]
        }
        if "type" in input_data.columns:
            drivers[n]["type"] = str(input_data["type"][n])
        if "diameter" in input_data.columns:
            drivers[n]["diameter"] = float(input_data["diameter"][n])
        if "lpf_frequency" in input_data.columns:
            drivers[n]["lpf_frequency"] = float(input_data["lpf_frequency"][n])
        if "hpf_frequency" in input_data.columns:
            drivers[n]["hpf_frequency"] = float(input_data["hpf_frequency"][n])
    print(drivers)

    data = {
        "panel": {
            "name": name,
            "dimensions": [panel_width, panel_depth, panel_height],
        },
        "drivers": drivers
    }

    # Export YAML, with lists (for coordinates) represented on one line
    def represent_list_flow(dumper, data):
        return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
    yaml.add_representer(list, represent_list_flow)

    with open(output_file, "w") as f:
        yaml.dump(data, f, sort_keys=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert panel layout from CSV to YAML")
    parser.add_argument("input_file", help="Path to input CSV file")
    parser.add_argument("--output-file", "-o", default=None, help="Path to output YAML file")
    parser.add_argument("--name", type=str, default="openwfs-v2a", help="Name of the panel layout")
    parser.add_argument("--panel-width", type=float, default=250.0, help="Width of the panel in mm")
    parser.add_argument("--panel-height", type=float, default=250.0, help="Height of the panel in mm")
    parser.add_argument("--panel-depth", type=float, default=100.0, help="Depth of the panel in mm")
    args = parser.parse_args()

    if args.output_file is None:
        args.output_file = args.input_file.rsplit(".", 1)[0] + ".yaml"

    main(input_file=args.input_file,
         output_file=args.output_file,
         name=args.name,
         panel_width=args.panel_width,
         panel_height=args.panel_height,
         panel_depth=args.panel_depth)
