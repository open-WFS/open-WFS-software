from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
import threading
from loguru import logger

from .layout import Room
from .source import Source
from .config import SpatialiserConfig

from signalflow import AudioGraph, AudioGraphConfig, SpatialEnvironment, AudioIn, RMS


class Spatialiser:
    def __init__(self,
                 config_name: str,
                 room_layout: str,
                 show_status: bool = False,
                 num_sources: int = 8):
        self.config = SpatialiserConfig.from_yaml(config_name)
        self.room = Room.from_yaml(room_layout)
        self.graph = None
        self.show_status = show_status
        self.num_sources = num_sources
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

        if self.show_status:
            self.graph.poll(2)

        self.spatial_environment = SpatialEnvironment()
        for speaker_index, driver in enumerate(self.room.drivers):
            position_m = driver.position * 0.001
            print(position_m)
            self.spatial_environment.add_speaker(speaker_index, *list(position_m))

        raw_input = AudioIn(self.num_sources)

        self.input_rms = RMS(raw_input)
        self.graph.add_node(self.input_rms)

        # Causes crash!
        # for source_index, source_audio in enumerate(raw_input):
        for source_index in range(self.num_sources):
            source = Source(source_index,
                            self.spatial_environment,
                            raw_input[source_index])
            self.sources.append(source)

        
        # create an OSC server
        dispatcher = Dispatcher()
        dispatcher.map("/source/*/xyz", self.handle_osc_set_source_position)
        dispatcher.set_default_handler(self.handle_osc)
        self.osc_server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", self.config.osc_port),
                                                           dispatcher)
        self.thread = threading.Thread(target=self.osc_server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        self.graph.clear()
        self.graph.destroy()
        self.graph = None
        self.sources = []

    def handle_osc_set_source_position(self, address, *args):
        # Spat OSC format: /source/*/xyz
        address_parts = address.split("/")

        # For compliance with Spat OSC format, assume numbering from 1
        source_index = int(address_parts[2]) - 1

        x, y, z = args
        logger.info("Set source %d position: %s %s %s" % (source_index, x, y, z))
        self.sources[source_index].position = [x, y, z]

    def handle_osc(self, address, *args):
        logger.warning("OSC address not handled: %s (%s)" % (address, args))

    
    def run_sound_check(self):
        """
        Run a sound check in which a short burst of white noise is played sequentially
        across all channels.
        """
        from signalflow import WhiteNoise, Impulse, ASREnvelope, Counter, ChannelPanner
        logger.info("Starting sound check...")
        logger.info("You should hear bursts of white noise played through each channel sequentially.")
        logger.info("Press ctrl-c to stop sound check.")
        source = WhiteNoise() * 0.25
        clock = Impulse(4)
        source = source * ASREnvelope(0.0, 0, 0.1, clock=clock)
        counter = Counter(clock, 0, self.num_speakers)
        panner = ChannelPanner(self.num_speakers, input=source, pan=counter)
        panner.play()