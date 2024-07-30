# OpenWFS: Spatialiser

This repository contains spatial panning utilities for OpenWFS, and a Python-based spatial panner.

## Usage instructions for Spat (Max/MSP)

Currently, this is the recommended approach for optimal WFS performance.

### 1. Install the system requirements

These instructions are for macOS, and assume you have already installed the [general OpenWFS requirements and AVB drivers](https://github.com/open-WFS/open-WFS-docs).

 - Install [BlackHole 64ch](https://existential.audio/blackhole/): This is used to route audio from your playback system to the panner. You can also use [Loopback](https://rogueamoeba.com/loopback/).
 - Install Max 8 and the [Spat](https://forum.ircam.fr/projects/detail/spat/) spatialisation library.
 - With Python 3.8 or above, run `pip3 install -r requirements.txt` from within this repo to install the Python scripting requirements.

### 2. Configure the spatial layout of your system

Measure and record the Cartesian x/y/z coordinates of each module of the OpenWFS array. All coordinates should be measured relative to a [0, 0, 0] origin determined by you; in general, a good origin is the centre of the listening space.

Enter the coordinates in the `module_layout` property of `spatialiser/constants.py`.

### 3. Run a sound check to confirm that the stream configuration is successful

This can be done with the [OpenWFS Spatialiser](https://github.com/open-WFS/open-WFS-spatialiser/) or a utility like Reaper.

#### Using the OpenWFS Spatialiser

 From within this repo, run:
 
 ```
 bin/run-spatialiser.py --sound-check
 ```

 You should a burst of pink noise played through each driver in turn.

### 4. Generate the coordinates for Spat

Output the driver coordinates in a format that Spat can read, to a file called `speaker-layout.txt`. From the top level of this repo:

```
python3 bin/generate-spat-layout max/speaker-layout.txt
```

### 5. Open Spat

- Open `max/OpenWFS Spat.maxpat`
- Configure the input to be `BlackHole 64ch`, and the output to be your Digiface or AVB aggregate device
- Start Max/MSP's audio

### 6. Begin playing audio

You should now be able to play spatialised audio through the system. Each audio channel of BlackHole corresponds to a different sound source, so audio played through Channel 1 will be routed to Source 1, and so forth.

### 7. Animate sound sources via OSC

Each sound source's spatial position can be controlled by sending OSC messages to the spatialiser. Note that, for consistency with Max/MSP Spat, sound sources are numbered from 1 upwards.

| OSC address | Parameters | Description |
|-------------|------------|-------------|
| `/source/<source_id>/xyz` | `x`, `y`, `z` | Set the [x, y, z] coordinate of the source, with positions in metres |

An example Python script demonstrating oscillating motion is provided in `bin/example-spatialiser-osc-client.py`.

---

## The Python spatial panner

An alternative panner for Python is currently in development. It is not recommended for use at present, as it lacks some of the WFS algorithms implemented in Spat.

The panner system:

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

The panner can be controlled by OSC, following the protocol described above.

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
