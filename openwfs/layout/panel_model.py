from __future__ import annotations
import os
import yaml
import argparse
from dataclasses import dataclass


@dataclass
class DriverModel:
    position: list[float]
    type: str
    diameter: float
    lpf_frequency: float | None = None
    hpf_frequency: float | None = None


@dataclass
class PanelModel:
    dimensions: tuple[float, float, float]
    name: str
    drivers: list[DriverModel]

    @classmethod
    def from_name(cls, name: str) -> PanelModel:
        base_path = os.path.dirname(os.path.abspath(__file__))
        layouts_path = os.path.join(base_path, "../../data/panel-layouts")
        file_path = os.path.join(layouts_path, f"{name}.yaml")
        file_path = os.path.normpath(file_path)

        return cls.from_yaml(file_path)

    @classmethod
    def from_yaml(cls, file_path: str):
        """
        Load panel layout from a YAML file.

        Args:
            file_path (str): Path to the YAML file.
        """
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        panel_data = data["panel"]

        drivers_data = data["drivers"]
        drivers = []
        for driver_info in drivers_data.values():
            driver = DriverModel(position=driver_info["position"],
                                 type=driver_info.get("type", "tweeter"),
                                 diameter=driver_info.get("diameter", 50.8),
                                 lpf_frequency=driver_info.get("lpf_frequency"),
                                 hpf_frequency=driver_info.get("hpf_frequency"))
            drivers.append(driver)

        panel_geometry = PanelModel(name=panel_data["name"],
                                    dimensions=panel_data["dimensions"],
                                    drivers=drivers)

        return panel_geometry

    def __str__(self):
        return f"PanelGeometry(name={self.name}, dimensions={self.dimensions}, drivers={self.drivers})"

    def dump(self):
        print(f"OpenWFS panel: {self.name}")
        print(f"Dimensions (W x H x D): {self.dimensions[0]} x {self.dimensions[1]} x {self.dimensions[2]} mm")
        print("Drivers:")
        for i, driver in enumerate(self.drivers):
            print(f" - {i}: position={driver.position}, type={driver.type}, diameter={driver.diameter} mm, "
                  f"LPF={driver.lpf_frequency if driver.lpf_frequency is not None else 'N/A'} Hz, "
                  f"HPF={driver.hpf_frequency if driver.hpf_frequency is not None else 'N/A'} Hz")

    def export_to_spat_layout(self, output_file: str):
        with open(output_file, "w") as fd:
            for driver in self.drivers:
                x, y = driver.position
                z = 0.0  # Assuming drivers are on a flat panel at z=0
                fd.write(f"{x} {y} {z}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load panel layout from a YAML file")
    parser.add_argument("yaml_file", help="Path to the panel layout YAML file")
    args = parser.parse_args()

    layout = PanelModel.from_yaml(args.yaml_file)
    layout.dump()