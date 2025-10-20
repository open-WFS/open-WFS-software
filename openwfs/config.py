from dataclasses import dataclass
from typing import Optional
import yaml
import os

class SpatialiserConfig:
    input_device_name: Optional[str] = None
    output_device_name: Optional[str] = None
    input_buffer_size: Optional[int] = None
    output_buffer_size: Optional[int] = None
    osc_port: int = 9130

    @classmethod
    def from_yaml(cls, file_path):
        if not os.path.exists(file_path):
            file_path = os.path.join("data", "spatialiser-config", "%s.yaml" % file_path)
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        
        config = SpatialiserConfig()
        config.input_device_name = data.get("input_device_name", None)
        config.output_device_name = data.get("output_device_name", None)
        config.input_buffer_size = data.get("input_buffer_size", None)
        config.output_buffer_size = data.get("output_buffer_size", None)

        return config
