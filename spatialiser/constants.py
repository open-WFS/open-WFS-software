import numpy as np
from dataclasses import dataclass

input_device_name = "BlackHole 64ch"
# input_device_name = "Loopback 2ch"
# output_device_name = "Model 12"
# output_device_name = "XMOS xCORE-200 MC (UAC2.0)"
# output_device_name = "XMOS x2"
# output_device_name = "BlackHole 64ch"
output_device_name = "Digiface AVB (24119914)"
# output_device_name = "openWFS Module v1:Audio Unit 0"
input_buffer_size = 256
output_buffer_size = 256

num_speakers = 96
num_speakers_per_module = 32
num_sources = 8
disable_lfe = False
disable_midi = False
crossover_frequency = 200

environment_radius_x = 0.5
environment_radius_y = 0.5
environment_radius_z = 0.5

@dataclass
class Module:
    position: list[float]
    rotation: float

module_layout = [
    Module([1.0, -0.5, 0.0], -1.0 * np.pi / 2),
    Module([-1.0, -0.5, 0.0], 1.0 * np.pi / 2),
    Module([0.0, 0.5, 0.0], 0),
    Module([0.0, -0.5, 0.5], 0),
]

source_colours = [
    [1.0, 0.0, 0.0, 1.0],
    [1.0, 0.5, 0.0, 1.0],
    [1.0, 1.0, 0.0, 1.0],
    [0.5, 1.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 1.0, 0.5, 1.0],
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 0.5, 1.0, 1.0],
    [0.0, 0.0, 1.0, 1.0],
    [0.5, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0],
]
