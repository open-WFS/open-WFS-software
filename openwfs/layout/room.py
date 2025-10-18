
import yaml
import argparse
from dataclasses import dataclass
from .panel import Panel
from .panel_model import PanelModel

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
            if "panel_model" not in panel_data:
                panel_data["panel_model"] = panel_model
            panel = Panel.from_dict(panel_data)
            panels.append(panel)

        return cls(name=name,
                   panel_model=panel_model,
                   dimensions=dimensions,
                   origin=origin,
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load room layout from a YAML file")
    parser.add_argument("yaml_file", help="Path to the room layout YAML file")
    parser.add_argument("--export-spat-layout", "-o", default=None, help="Path to export Spat layout file")
    args = parser.parse_args()

    room = Room.from_yaml(args.yaml_file)
    room.dump()

    if args.export_spat_layout:
        room.export_to_spat_layout(args.export_spat_layout)
        print(f"Exported Spat layout to {args.export_spat_layout}")
