import numpy as np
from dataclasses import dataclass

input_device_name = "BlackHole 64ch"
# input_device_name = "Loopback 2ch"
# output_device_name = "Model 12"
# output_device_name = "XMOS xCORE-200 MC (UAC2.0)"
# output_device_name = "XMOS x2"
# output_device_name = "BlackHole 64ch"
output_device_name = "Digiface AVB (24119914)"
input_buffer_size = 256
output_buffer_size = 256

num_speakers = 64
num_sources = 1

@dataclass
class Module:
    position: list[float]
    rotation: float

module_layout = [
    Module([0.0, 0.0, 0.0], 0),
    Module([1.25, 0, 0.0], -1.0 * np.pi / 2),
]
