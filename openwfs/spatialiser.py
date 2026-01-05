from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
import threading
from loguru import logger

from .layout import Room
from .source import Source
from .config import SpatialiserConfig

from signalflow import *


class Spatialiser:
    def __init__(self,
                 config_name: str,
                 room_layout: str,
                 show_status: bool = False,
                 num_sources: int = 8,
                 gain: float = 0.0):
        self.config = SpatialiserConfig.from_yaml(config_name)
        self.room = Room.from_yaml(room_layout)
        self.graph = None
        self.show_status = show_status
        self.num_sources = num_sources
        self.gain = gain
        self.num_speakers = len(self.room.drivers)
        self.sources: list[Source] = []

    def start(self):
        # Create the AudioGraph
        self.graph_config = AudioGraphConfig()
        self.graph_config.input_buffer_size = self.config.input_buffer_size
        self.graph_config.output_buffer_size = self.config.output_buffer_size
        self.graph_config.input_device_name = self.config.input_device_name
        self.graph_config.output_device_name = self.config.output_device_name
        self.graph = AudioGraph(config=self.graph_config)
        self.graph.poll(1)

        if self.show_status:
            self.graph.poll(1)

        self.spatial_environment = SpatialEnvironment()
        for speaker_index, driver in enumerate(self.room.drivers):
            self.spatial_environment.add_speaker(speaker_index, *list(driver.position * 0.001))

        raw_input = AudioIn(self.num_sources)

        self.input_rms = RMS(raw_input)
        self.graph.add_node(self.input_rms)
        self.output_bus = Bus(self.num_speakers)
        self.output_bus_attenuated = db_to_amplitude(self.gain) * self.output_bus
        self.limiter = Clip(self.output_bus_attenuated, min=-0.1, max=0.1)
        self.graph.play(self.limiter)

        # Causes crash!
        # for source_index, source_audio in enumerate(raw_input):
        for source_index in range(self.num_sources):
            source = Source(source_index,
                            self.spatial_environment,
                            raw_input[source_index],
                            self.output_bus)
            self.sources.append(source)

        
        # create an OSC server
        dispatcher = Dispatcher()
        dispatcher.map("/source/*/xyz", self.handle_osc_set_source_position)
        dispatcher.map("/source/*/radius", self.handle_osc_set_source_radius)
        dispatcher.set_default_handler(self.handle_osc)
        self.osc_server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", self.config.osc_port),
                                                           dispatcher)
        self.thread = threading.Thread(target=self.osc_server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        # For some reason, calling these lines causes the application to hang sometimes.
        # self.osc_server.shutdown()
        self.graph.clear()
        self.graph.destroy()
        self.sources = []
        

    def handle_osc_set_source_position(self, address, *args):
        # Spat OSC format: /source/*/xyz
        # For compliance with Spat OSC format, assume numbering from 1
        source_index = int(address.split("/")[2]) - 1

        x, y, z = args
        logger.debug("Set source %d position: %s %s %s" % (source_index, x, y, z))
        self.sources[source_index].position = [x, y, z]
    
    def handle_osc_set_source_radius(self, address, *args):
        # Spat OSC format: /source/*/radius
        source_index = int(address.split("/")[2]) - 1

        radius = args[0]
        logger.debug("Set source %d radius: %s" % (source_index, radius))
        self.sources[source_index].radius = radius

    def handle_osc(self, address, *args):
        logger.warning("OSC address not handled: %s (%s)" % (address, args))

    
    def run_sound_check(self,
                        type: str = "pinknoise",
                        interval: float = 0.25):
        """
        Run a sound check in which a short burst of white noise is played sequentially
        across all channels.
        """
        from signalflow import WhiteNoise, PinkNoise, Impulse, ASREnvelope, Counter, ChannelPanner
        logger.info("Starting sound check...")
        logger.info("You should hear bursts of white noise played through each channel sequentially.")
        logger.info("Press ctrl-c to stop sound check.")
        if type == "whitenoise":
            source = WhiteNoise()
        elif type == "pinknoise":
            source = PinkNoise()
        source = source * 0.25
        clock = Impulse(1 / interval)
        source = source * ASREnvelope(0.0, 0, 0.1, clock=clock)
        counter = Counter(clock, 0, self.num_speakers)
        panner = ChannelPanner(self.num_speakers, input=source, pan=counter)
        panner.play()
