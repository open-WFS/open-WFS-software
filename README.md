# OpenWFS: Spatialiser

This repository contains the spatial panner for OpenWFS. This process:

 - contains spatial configuration for a given WFS speaker system, and other global properties
 - reads real-time audio input from a loopback audio device (typically [Blackhole](https://existential.audio/blackhole/) 64ch), with each mono channel corresponding to a single sound object (a "source")
 - receives real-time metadata corresponding to each source's XYZ position in space, either via MIDI or OSC
 - generates multi-channel audio output, in which each source is spatialised appropriately

## Usage

Python 3.9+ is required. 

 - To install requirements: `pip install -r requirements.txt`
 - To update configuration, edit `spatialiser/constants.py`
 - To run the spatialiser: `./run-spatialiser.py`

## Panner controls

### OSC

Each sound source's spatial position can be controlled by sending MIDI messages to the spatialiser.

| OSC address | Parameters | Description |
|-------------|------------|-------------|
| `/source/<source_id>/xyz` | `x`, `y`, `z` | Set the [x, y, z] coordinate of the source, with positions in metres |

### MIDI

The spatial position of a source can be controlled via MIDI messages. The spatialiser listens for MIDI on the device specified in `midi_input_device_name` in `constants.py`.

The MIDI channel should correspond to the index of the sound source to be modulated (allowing up to 16 sound sources). The position is controlled by control change messages, with the following implementation.

| CC# | Parameter | Minimum value | Maximum value |
|-----|-----------|---------------|---------------|
| 0 | X position | `-environment_radius_x` | `environment_radius_x` |
| 1 | Y position | `-environment_radius_y` | `environment_radius_y` |
| 2 | Z position | `-environment_radius_z` | `environment_radius_z` |
| 3 | X LFO amplitude | 0m | 1m |
| 4 | X LFO frequency | 0.01Hz | 10Hz |
| 5 | Y LFO amplitude | 0m | 1m |
| 6 | Y LFO frequency | 0.01Hz | 10Hz |

Positional value ranges are determined by the `environment_radius_x`, `environment_radius_y` and `environment_radius_z` constants in `constants.py`. Sending a CC value of 0 corresponds to an x-position of `-environment_radius_x`, and a CC value of 127 corresponds to `+environment_radius_x`.
