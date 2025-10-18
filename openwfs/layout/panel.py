from dataclasses import dataclass
from .panel_model import PanelModel


@dataclass
class Panel:
    index: int
    model: PanelModel
    position: list[float]
    rotation: list[float]

    @classmethod
    def from_dict(cls, data: dict):
        panel = cls(index=data["index"],
                    model=data["panel_model"],
                    position=data["position"],
                    rotation=data["rotation"])
        return panel

    def dump(self):
        print(f"Panel {self.index}")
        print(f" - model: {self.model.name}")
        print(f" - position: {self.position}")
        print(f" - rotation: {self.rotation}")
