from .module import Module
import numpy as np

#--------------------------------------------------------------------------------
# The names of the audio input and output devices to use.
# Note that partial name matches are allowed, so you can just specify the prefix.
#--------------------------------------------------------------------------------
input_device_name = "BlackHole 64ch"
output_device_name = "Digiface AVB"
midi_input_device_name = "IAC Driver Bus 1"

#--------------------------------------------------------------------------------
# Port used to listen for OSC messages to set source positions.
#--------------------------------------------------------------------------------
osc_port = 9130

#--------------------------------------------------------------------------------
# The input and output audio buffer size, in samples.
#--------------------------------------------------------------------------------
input_buffer_size = 256
output_buffer_size = 256

#--------------------------------------------------------------------------------
# The number of drivers to use per module.
# The driver layout is read from `spatialiser/data/openwfs_driver_layout_v2.csv`
#--------------------------------------------------------------------------------
num_speakers_per_module = 32

#--------------------------------------------------------------------------------
# The number of sound sources to pan.
#--------------------------------------------------------------------------------
num_sources = 8

#--------------------------------------------------------------------------------
# The centre coordinates of each OpenWFS module, in metres.
# For the Y-axis, positive values are in front of the listener.
#--------------------------------------------------------------------------------
module_layout_horseshoe = [
    Module([-1.05 - 0.15,  0.5, 1.0], -np.pi/2),
    Module([-0.533,         1.0, 1.0], 0),
    Module([0.533,          1.0, 1.0], 0),
    Module([1.05 + 0.15,   0.5, 1.0], np.pi/2),
]

#--------------------------------------------------------------------------------
# Octagon of 8 modules (1.05m wide, 0.16m tall, 0.18m deep) around the listener.
# Front faces meet edge-to-edge, forming a regular octagon with 1.05m sides:
#   front-face apothem = 1.05 / (2 * tan(pi/8))  = 1.2675m
#   centroid radius    = 1.2675 + 0.18 / 2        = 1.3575m
#   diagonal offset    = 1.3575 * cos(pi/4)       = 0.9599m
# Ordered clockwise from the front module (viewed from above).
#--------------------------------------------------------------------------------
module_layout_octagon = [
    Module([ 0.0,     1.3575, 1.0],  0),
    Module([ 0.9599,  0.9599, 1.0],  np.pi/4),
    Module([ 1.3575,  0.0,    1.0],  np.pi/2),
    Module([ 0.9599, -0.9599, 1.0],  3*np.pi/4),
    Module([ 0.0,    -1.3575, 1.0],  np.pi),
    Module([-0.9599, -0.9599, 1.0], -3*np.pi/4),
    Module([-1.3575,  0.0,    1.0], -np.pi/2),
    Module([-0.9599,  0.9599, 1.0], -np.pi/4),
]

module_layout = module_layout_octagon


#--------------------------------------------------------------------------------
# If the LFE channel is enabled, a low-passed mono mixdown of the output
# content is sent to this channel index.
#--------------------------------------------------------------------------------
num_speakers = num_speakers_per_module * len(module_layout)
lfe_channel_index = num_speakers - 1
crossover_frequency_lpf = 180
crossover_frequency_hpf = 30

#--------------------------------------------------------------------------------
# Activate/deactivate various features.
#  - lfe: relay a bass channel mono mixdown to the specified channel
#  - midi: receive real-time MIDI controls to set the source locations
#  - audio: enable/disable audio
#  - randomise_lfos: add random positional oscillations to each source
#--------------------------------------------------------------------------------
disable_lfe = True
disable_midi = False
disable_audio = False
randomise_lfos = False

#--------------------------------------------------------------------------------
# Environment size, in metres
#--------------------------------------------------------------------------------
environment_radius_x = 2.0
environment_radius_y = 1.0
environment_radius_z = 0.5

#--------------------------------------------------------------------------------
# Source colours for 3D visualiser
#--------------------------------------------------------------------------------
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
