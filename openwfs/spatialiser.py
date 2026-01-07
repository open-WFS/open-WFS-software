from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
import threading
import time

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
        logger.info("Initialising OpenWFS spatialiser...")
        self.config = SpatialiserConfig.from_yaml(config_name)
        self.room = Room.from_yaml(room_layout)
        logger.info("Loaded room layout: %s" % self.room)
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
        
        def show_graph_status():
            while True:
                time.sleep(5)
                logger.info(self.graph.status)

        if self.show_status:
            thread = threading.Thread(target=show_graph_status, daemon=True)
            thread.start()

        self.spatial_environment = SpatialEnvironment()
        for speaker_index, driver in enumerate(self.room.drivers):
            self.spatial_environment.add_speaker(speaker_index, *list(driver.position * 0.001))

        logger.info("Creating %d sources..." % self.num_sources)
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
        dispatcher.map("/global/gain", self.handle_osc_global_gain)
        dispatcher.map("/source/*/xyz", self.handle_osc_set_source_position)
        dispatcher.map("/source/*/radius", self.handle_osc_set_source_radius)
        dispatcher.map("/source/*/algorithm", self.handle_osc_set_source_algorithm)
        dispatcher.map("/source/*/solo", self.handle_osc_source_solo)
        dispatcher.map("/source/*/mute", self.handle_osc_source_mute)
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

    @property
    def any_source_is_soloed(self) -> bool:
        for source in self.sources:
            if source.is_soloed:
                return True
        return False
    
    def handle_osc_global_gain(self, address, *args):
        gain_db = args[0]
        logger.info("Set global gain: %s dB" % gain_db)
        self.set_gain(gain_db)

    def handle_osc_set_source_position(self, address, *args):
        # Spat OSC format: /source/*/xyz
        # For compliance with Spat OSC format, assume numbering from 1
        source_index = int(address.split("/")[2]) - 1

        x, y, z = args
        # logger.debug("Set source %d position: %s %s %s" % (source_index, x, y, z))
        self.sources[source_index].position = [x, y, z]
    
    def handle_osc_set_source_radius(self, address, *args):
        # Spat OSC format: /source/*/radius
        source_index = int(address.split("/")[2]) - 1

        radius = args[0]
        logger.debug("Set source %d radius: %s" % (source_index, radius))
        self.sources[source_index].radius = radius
    
    def handle_osc_set_source_algorithm(self, address, *args):
        source_index = int(address.split("/")[2]) - 1

        algorithm = args[0]
        logger.debug("Set source %d algorithm: %s" % (source_index, algorithm))
        self.sources[source_index].algorithm = algorithm

    def handle_osc_source_solo(self, address, *args):
        source_index = int(address.split("/")[2]) - 1
        solo = args[0]
        source = self.sources[source_index]

        if (solo and source.is_soloed) or (not solo and not source.is_soloed):
            # No-op. This may happen as the panner and plugin are not necessarily in sync.
            return

        if solo:
            logger.info("Solo source %d" % source_index)
            for other_source in self.sources:
                if other_source.is_soloed:
                    other_source.is_soloed = False
            self.output_bus.clear_inputs()
            time.sleep(0.05)
            if not source.is_muted:
                self.output_bus.add_input(source.panner)
                source.is_soloed = True
        else:
            logger.info("Un-solo source %d" % source_index)
            self.output_bus.clear_inputs()
            time.sleep(0.05)
            for other_source in self.sources:
                if not other_source.is_muted:
                    self.output_bus.add_input(other_source.panner)
            source.is_soloed = False
    
    def handle_osc_source_mute(self, address, *args):
        source_index = int(address.split("/")[2]) - 1
        mute = args[0]
        source = self.sources[source_index]

        if (mute and source.is_muted) or (not mute and not source.is_muted):
            # No-op. This may happen as the panner and plugin are not necessarily in sync.
            return

        if mute:
            logger.info("Mute source %d" % source_index)
            if (not self.any_source_is_soloed) or source.is_soloed:
                self.output_bus.remove_input(source.panner)
            source.is_muted = True
        else:
            logger.info("Un-mute source %d" % source_index)
            if (not self.any_source_is_soloed) or source.is_soloed:
                self.output_bus.add_input(source.panner)
            source.is_muted = False

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

    def get_gain(self) -> float:
        return self.gain
    
    def set_gain(self, gain: float):
        self.gain = gain
        if self.output_bus_attenuated is not None:
            self.output_bus_attenuated.input0 = db_to_amplitude(gain)