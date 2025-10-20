
import os
import yaml
import argparse
from dataclasses import dataclass
from .panel import Panel, Driver
from .panel_model import PanelModel
import numpy as np
import matplotlib.pyplot as plt


@dataclass
class Room:
    name: str
    panel_model: PanelModel
    dimensions: list[float]
    origin: list[float]
    panels: list[Panel]

    @classmethod
    def from_yaml(cls, file_path: str):
        if not os.path.exists(file_path):
            file_path = os.path.join("data", "room-layouts", "%s.yaml" % file_path)

        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        name = data["name"]
        panel_model = PanelModel.from_name(data["panel_model"])
        dimensions = data["dimensions"]
        origin = data["origin"]

        panels = []
        for index, panel_data in enumerate(data["panels"]):
            panel_data["index"] = index
            panel_data["position"] = np.array(panel_data["position"]) * 1000
            panel_data["rotation"] = np.radians(panel_data["rotation"])
            if "panel_model" not in panel_data:
                panel_data["panel_model"] = panel_model
            panel = Panel.from_dict(panel_data)
            panels.append(panel)

        return Room(name=name,
                    panel_model=panel_model,
                    dimensions=np.array(dimensions) * 1000,
                    origin=np.array(origin) * 1000,
                    panels=panels)

    def dump(self):
        print("Room name:", self.name)
        print("Dimensions (W x H x D):", self.dimensions)
        print("Origin:", self.origin)
        print("Panels:")
        for i, panel in enumerate(self.panels):
            print(f" - Panel {i}:")
            print(f"   - Model: {panel.model.name}")
            print(f"   - Position: {panel.position}")
            print(f"   - Rotation: {panel.rotation}")

    def export_spat_layout(self, output_file: str):
        with open(output_file, "w") as f:
            f.write(f"/speakers/xyz ")
            for panel in self.panels:
                for driver in panel.drivers:
                    position = driver.position / 1000.0  # Convert to meters
                    f.write(f"{position[0]:.3f} {position[1]:.3f} {position[2]:.3f} ")
            f.write("\n")
            f.write(f"/speaker/*/direction/xy 0 -1\n")

    def get_drivers(self):
        drivers = []
        for panel in self.panels:
            drivers += panel.drivers
        return drivers

    drivers = property(get_drivers)

    def export_complete_room_layout(self, output_file: str):
        # Export the complete room layout to YAML, including room properties: name, dimensions, origin
        # For each panel: panel ID, and a list of drivers, including exact positions in mm, orientation in degrees, and diameter in mm
        room_data = {
            "name": self.name,
            "dimensions": (self.dimensions / 1000).tolist(),
            "origin": (self.origin / 1000).tolist(),
            "panels": []
        }

        for panel in self.panels:
            panel_data = {
                "index": panel.index,
                "drivers": []
            }
            for driver in panel.drivers:
                driver_data = {
                    "index": driver.index,
                    "position": (driver.position / 1000).tolist(),
                    "diameter": driver.model.diameter / 1000
                }
                panel_data["drivers"].append(driver_data)
            room_data["panels"].append(panel_data)

        # Export YAML, with lists of numbers represented on one line, but lists of dicts on separate lines
        def represent_list_flow(dumper, data):
            # Only use flow style for lists containing only numbers (int/float)
            if data and all(isinstance(item, (int, float)) for item in data):
                return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
            else:
                return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=False)
        yaml.add_representer(list, represent_list_flow)

        with open(output_file, "w") as f:
            yaml.dump(room_data, f, sort_keys=False)

    def visualise(self):
        from ..visualisation import render_cuboids_3d, Cuboid

        cuboids = []
        # Constructor for Cuboid:
        # (self, position, dimensions, rotation_angles=(0, 0, 0), color='blue', alpha=0.7):
        for panel in self.panels:
            print(panel.model.dimensions, panel.rotation)
            cuboid = Cuboid(position=panel.position,
                            dimensions=panel.model.dimensions,
                            rotation_angles=panel.rotation,
                            color='cyan')
            cuboids.append(cuboid)

        render_cuboids_3d(cuboids,
                          title=f"Room Layout: {self.name}",
                          xlim=(-self.dimensions[0]/2, self.dimensions[0]/2),
                          ylim=(-self.dimensions[1]/2, self.dimensions[1]/2),
                          zlim=(0, self.dimensions[2]))
        
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load room layout from a YAML file")
    parser.add_argument("yaml_file", help="Path to the room layout YAML file")
    parser.add_argument("--visualise", "-v", action="store_true", help="Show a 3D visualisation of the room layout")
    parser.add_argument("--export-spat-layout", "-o", default=None, help="Path to export Spat layout file")
    parser.add_argument("--export-complete-layout", "-c", default=None, help="Path to export complete room layout YAML file")
    args = parser.parse_args()

    if not os.path.exists(args.yaml_file):
        args.yaml_file = os.path.join(os.path.dirname(__file__), "../../data/room-layouts/%s.yaml" % args.yaml_file)

    room = Room.from_yaml(args.yaml_file)
    room.dump()

    if args.visualise:
        room.visualise()

    if args.export_spat_layout:
        room.export_spat_layout(args.export_spat_layout)
        print(f"Exported Spat layout to {args.export_spat_layout}")
    
    if args.export_complete_layout:
        room.export_complete_room_layout(args.export_complete_layout)
        print(f"Exported complete room layout to {args.export_complete_layout}")
