from .module import Module

#--------------------------------------------------------------------------------
# The names of the audio input and output devices to use.
# TODO: input_device_name is currently not honoured due as it is not supported
# in SignalFlow. The system's default audio input device is used instead.
#--------------------------------------------------------------------------------
input_device_name = "BlackHole 64ch"
output_device_name = "Digiface AVB (24119914)"
# output_device_name = "BlackHole 64ch"
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
num_sources = 2

#--------------------------------------------------------------------------------
# The centre coordinates of each OpenWFS module, in metres.
# For the Y-axis, positive values are in front of the listener.
#--------------------------------------------------------------------------------
module_layout = [
    Module([-1.598, 4.0, 0.0], 0),
    Module([-0.533, 4.0, 0.0], 0),
    Module([0.533, 4.0, 0.0], 0),
    Module([1.598, 4.0, 0.0], 0),
]

num_speakers = num_speakers_per_module * len(module_layout)

#--------------------------------------------------------------------------------
# If the LFE channel is enabled, a low-passed mono mixdown of the output 
# content is sent to this channel index.
#--------------------------------------------------------------------------------
lfe_channel_index = num_speakers - 1
crossover_frequency_lpf = 180
crossover_frequency_hpf = 300

#--------------------------------------------------------------------------------
# Activate/deactivate various features.
#  - lfe: relay a bass channel mono mixdown to the specified channel
#  - midi: receive real-time MIDI controls to set the source locations
#  - audio: enable/disable audio 
#  - randomise_lfos: add random positional oscillations to each source
#--------------------------------------------------------------------------------
disable_lfe = True
disable_midi = True
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
