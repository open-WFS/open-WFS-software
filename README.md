# OpenWFS: Spatialiser

This repository contains spatial panning utilities for OpenWFS, and a Python-based spatial panner.

## Usage instructions for Spat (Max/MSP)

Currently, this is the recommended approach for optimal WFS performance.

### 1. Install the system requirements

These instructions are for macOS, and assume you have already installed the [general OpenWFS requirements and AVB drivers](https://github.com/open-WFS/open-WFS-docs).

 - Install [BlackHole 64ch](https://existential.audio/blackhole/): This is used to route audio from your playback system to the panner. You can also use [Loopback](https://rogueamoeba.com/loopback/).
 - Install Max 8 and the [Spat](https://forum.ircam.fr/projects/detail/spat/) spatialisation library.
 - With Python 3.9 or above:
 
 ```bash
 # Create a virtual environment
 python3 -m venv .venv

 # Activate the virtual environment
 . .venv/bin/activate

 # Install the openwfs package and requirements, in editable mode
 pip3 install -e .
 ```

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
python3 bin/generate-spat-layout.py max/speaker-layout.txt
```

### 5. Open Spat

- Open `max/OpenWFS Spat.maxpat`
- Configure the input to be `BlackHole 64ch`, and the output to be your Digiface/HDSPe or AVB aggregate device
- Update the Max patch with the current number of speakers (for example, 128). This should be done in 3 places:
  - spat5.wfs~ @sources 4 @speakers **128** @mc 1
  - spat5.viewer @initwith "/source/number 4, /speaker/number **128**
  - spat5.cascade~ @channels **128** @mc 1
- Click the "dump" button to read the layout configuration
- Start Max/MSP's audio

### 6. Begin playing audio

You should now be able to play spatialised audio through the system. Each audio channel of BlackHole corresponds to a different sound source, so audio played through Channel 1 will be routed to Source 1, and so forth.

### 7. Move sound sources via OSC

Each sound source's spatial position can be controlled by sending OSC messages to the spatialiser. Note that, for consistency with Max/MSP Spat, sound sources are numbered from 1 upwards.

| OSC address | Parameters | Description |
|-------------|------------|-------------|
| `/source/<source_id>/xyz` | `x`, `y`, `z` | Set the [x, y, z] coordinate of the source, with positions in metres |

An example Python script demonstrating oscillating motion is provided in `bin/example-spatialiser-osc-client.py`.

---

## Troubleshooting and gotchas

- If you’re trying to route audio through BlackHole but not hearing anything, try changing the system volume to BlackHole and check if the volume is turned up. This seemed to happen a lot on the studio Mac Mini.
- In Spat’s viewer, be sure to check the Z position of each sound source (in the xz viewer, accessed with the cog icon); by default, each sound source is on the floor (z=0), whereas the speaker array is at listening height. If you want to change the
- In Spat if the sound source is BEHIND the listener (or behind the array), note that it switches the spatialisation mode for the affected drivers. I don’t think this is configurable, and may not be such an issue in a ring format.
