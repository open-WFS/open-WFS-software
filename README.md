# OpenWFS: Spatialiser

This repository contains the spatial panner for OpenWFS. This process:

 - contains spatial configuration for a given WFS speaker system, and other global properties
 - reads real-time audio input from a loopback audio device (typically [Blackhole](https://existential.audio/blackhole/) 64ch), with each mono channel corresponding to a single sound object (a "source")
 - reads real-time metadata corresponding to each source's XYZ position in space, either via MIDI or OSC
 - generates multi-channel audio output, in which each source is spatialised appropriately

## Usage

Python 3.9+ is required. 

 - To install requirements: `pip install -r requirements.txt`
 - To update configuration, edit `spatialiser/constants.py`
 - To run the spatialiser: `./run-spatialiser.py`
