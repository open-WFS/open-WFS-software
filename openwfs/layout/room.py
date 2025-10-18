
import yaml
import argparse
from dataclasses import dataclass
from .panel import Panel
from .panel_model import PanelModel
import numpy as np


@dataclass
class Room:
    name: str
    panel_model: PanelModel
    dimensions: list[float]
    origin: list[float]
    panels: list[Panel]

    @classmethod
    def from_yaml(cls, file_path: str):
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
            if "panel_model" not in panel_data:
                panel_data["panel_model"] = panel_model
            panel = Panel.from_dict(panel_data)
            panels.append(panel)

        return cls(name=name,
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

    def visualise(self):
        from ..visualisation import render_cuboids_3d, Cuboid

        cuboids = []
        # Constructor for Cuboid:
        # (self, position, dimensions, rotation_angles=(0, 0, 0), color='blue', alpha=0.7):
        for panel in self.panels:
            print(panel.model.dimensions)
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
        import matplotlib.pyplot as plt
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load room layout from a YAML file")
    parser.add_argument("yaml_file", help="Path to the room layout YAML file")
    parser.add_argument("--visualise", "-v", action="store_true", help="Show a 3D visualisation of the room layout")
    parser.add_argument("--export-spat-layout", "-o", default=None, help="Path to export Spat layout file")
    args = parser.parse_args()

    room = Room.from_yaml(args.yaml_file)
    room.dump()

    if args.visualise:
        room.visualise()

    if args.export_spat_layout:
        room.export_to_spat_layout(args.export_spat_layout)
        print(f"Exported Spat layout to {args.export_spat_layout}")
