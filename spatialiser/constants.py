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

num_speakers = 128
num_speakers_per_module = 16
num_sources = 8
disable_lfe = False
disable_midi = False
disable_audio = False
crossover_frequency_lpf = 400
crossover_frequency_hpf = 400

environment_radius_x = 1.0
environment_radius_y = 1.0
environment_radius_z = 0.5

@dataclass
class Module:
    position: list[float]
    rotation: float

# Y: +ve is front
# Y backwards: 45mm + 110mm + 1066mm
module_layout = [
    Module([0.99, 0.533, 0.0], -1.0 * np.pi / 2),      # right front - DONE
    Module([0.99, -0.533, 0.0], -1.0 * np.pi / 2),  # right rear - DONE
    Module([0.533, 0.0, 0.6], 0),  # top right - DONE
    Module([-0.533, 0.0, 0.6], 0),  # top left - DONE
    Module([-0.533, 1.221, 0.0], 0),  # centre left - DONE
    Module([-0.99, 0.533, 0.0], 1.0 * np.pi / 2),  # left front - DONE
    Module([-0.99, -0.533, 0.0], 1.0 * np.pi / 2),  # left rear - DONE
    Module([0.533, 1.221, 0.0], 0),                    # centre right - DONE
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
