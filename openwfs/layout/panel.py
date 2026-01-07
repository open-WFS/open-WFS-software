from dataclasses import dataclass
from .panel_model import PanelModel, DriverModel
import numpy as np

@dataclass
class Driver:
    index: int
    model: DriverModel
    position: list[float]
    rotation: list[float]

@dataclass
class Panel:
    index: int
    model: PanelModel
    position: np.ndarray
    rotation: np.ndarray
    is_muted: bool = False
    is_soloed: bool = False

    def get_drivers(self):
        drivers = []
        for driver_index, driver_model in enumerate(self.model.drivers):

            panel_centroid = np.array([
                self.model.dimensions[0] / 2,
                self.model.dimensions[1] / 2,
            ])

            # Driver positions are stored [x, y] relative to the front face of the panel.
            # Convert to world xyz coordinates.
            driver_position_normalised = driver_model.position - panel_centroid

            driver = Driver(index=driver_index,
                            model=driver_model,
                            position=np.array([
                                self.position[0] + np.cos(self.rotation[2]) * driver_position_normalised[0],
                                self.position[1] + np.sin(self.rotation[2]) * driver_position_normalised[0],
                                self.position[2] + driver_position_normalised[1],
                            ]),
                            rotation=self.rotation)
            drivers.append(driver)
        return drivers
    
    drivers = property(get_drivers)

    @classmethod
    def from_dict(cls, data: dict):
        panel = cls(index=data["index"],
                    model=data["panel_model"],
                    position=np.array(data["position"]),
                    rotation=np.array(data["rotation"]))
        return panel

    def dump(self):
        print(f"Panel {self.index}")
        print(f" - model: {self.model.name}")
        print(f" - position: {self.position}")
        print(f" - rotation: {self.rotation}")
