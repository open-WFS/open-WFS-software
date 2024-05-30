import time
import mido
import random
import logging
import threading
import numpy as np
import pandas as pd
from signalflow import *
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from .constants import input_device_name, output_device_name, num_speakers, input_buffer_size, output_buffer_size
from .constants import module_layout, num_sources, num_speakers_per_module, disable_lfe
from .constants import environment_radius_x, environment_radius_y, environment_radius_z, source_colours, disable_midi
from .constants import crossover_frequency
from .source import SpatialSource

logger = logging.getLogger(__name__)


class SpatialSpeaker:
    pass


class Spatialiser:
    def __init__(self, osc_port: int = 9130, show_cpu: bool = False):
        """
        Args:
            osc_port: The port to listen for OSC messages on. Default is 9130, which is the port used by the
                       source-viewer node application.
            show _cpu: If True, show CPU usage in the console.
        """

        self.is_running = False

        # create an OSC server
        dispatcher = Dispatcher()
        dispatcher.map("/source/*/xyz", self.handle_osc_set_source_position)
        dispatcher.set_default_handler(self.handle_osc)
        self.osc_server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", osc_port),
                                                           dispatcher)

        # Start listening for MIDI events
        if not disable_midi:
            inport = mido.open_input(name="IAC Driver Bus 1")
            inport.callback = self.handle_midi_message

        # --------------------------------------------------------------------------------
        # Visualiser: General setup
        # --------------------------------------------------------------------------------
        self.visualiser = SimpleUDPClient("127.0.0.1", 9129)
        self.visualiser.send_message("/grid/xy/on", [1])
        time.sleep(0.1)
        self.visualiser.send_message("/grid/size", [4])
        self.visualiser.send_message("/grid/section/size", [1])
        self.visualiser.send_message("/grid/subdiv/num", [10])
        time.sleep(0.1)
        self.visualiser.send_message("/source/size", [30.0])
        self.visualiser.send_message("/source/fade", [0])

        # --------------------------------------------------------------------------------
        # Audio: Add speakers
        # --------------------------------------------------------------------------------
        self.speakers = []
        self.num_speakers = num_speakers

        self.visualiser.send_message("/speaker/number", [num_speakers])
        time.sleep(0.2)
        self.visualiser.send_message("/speaker/size", [30.0])
        time.sleep(0.1)

        speaker_layout = pd.read_csv("../../Data/allspeaker_pos_v2.csv")
        mean_speaker_x = (speaker_layout.x.max() + speaker_layout.x.min()) / 2
        mean_speaker_y = (speaker_layout.y.max() + speaker_layout.y.min()) / 2
        speaker_layout.x = speaker_layout.x - mean_speaker_x
        speaker_layout.y = speaker_layout.y - mean_speaker_y

        for module in module_layout:
            for row_index, speaker in list(speaker_layout.iterrows())[:num_speakers_per_module]:
                module_speaker_x = module.position[0] + np.cos(module.rotation) * (speaker.x * 0.001)
                module_speaker_y = module.position[1] + np.sin(module.rotation) * (speaker.x * 0.001)
                module_speaker_z = module.position[2] + speaker.y * 0.001
                self.add_speaker([module_speaker_x,
                                  module_speaker_y,
                                  module_speaker_z])

        # --------------------------------------------------------------------------------
        # Audio: Add sources
        # --------------------------------------------------------------------------------
        self.sources = []
        self.add_sources()

        # this has to be called after sources have been created
        time.sleep(0.1)
        self.visualiser.send_message("/source/numDisplay", [1])

        # start_dust_process()

    def run_animation_thread(self):
        while self.is_running:
            delta = 0.02
            for source in self.sources:
                source.tick(delta)
                source.update_visualisation()
                source.update_panner()
            time.sleep(delta)

    def run_osc_thread(self):
        self.osc_server.serve_forever()

    def start(self):
        if self.is_running:
            return
        self.is_running = True

        self.graph.start()
        self.thread = threading.Thread(target=self.run_osc_thread)
        self.thread.daemon = True
        self.thread.start()

        self.animation_thread = threading.Thread(target=self.run_animation_thread)
        self.animation_thread.daemon = True
        self.animation_thread.start()

    def add_speaker(self, position: list):
        index = len(self.speakers)
        logger.info("Add speaker %d: %s" % (index, position))
        # self.env.add_speaker(index, *position)
        self.visualiser.send_message("/speaker/%d/xyz" % (index + 1), position)
        speaker = SpatialSpeaker()
        self.speakers.append(speaker)

    def add_source(self, index: int, position: list, color: list):
        logger.info("Add source: %s" % position)
        index_1indexed = index + 1

        self.visualiser.send_message("/source/number", [index_1indexed])
        time.sleep(0.1)
        self.visualiser.send_message("/source/%d/color" % index_1indexed, color)

        source = SpatialSource(index, position, self.visualiser)
        source.update_visualisation()


        # source.random_panner = (WhiteNoise([5] * self.num_speakers, interpolate=False) ** 5) * 5.0 * self.input_channels[index]
        # source.random_panner.play()

        # num_dust_channels = 50
        # dust = (RandomImpulse([3] * num_dust_channels) * (WhiteNoise() ** 4) * 0.1)
        # dust_cutoff = [random.uniform(8000, 14000) for n in range(num_dust_channels)]
        # dust_resonance = [random.uniform(0.4, 0.8) for n in range(num_dust_channels)]
        # dust = SVFilter(dust, "high_pass", dust_cutoff, resonance=dust_resonance)
        # dust.play()

        self.sources.append(source)

    def add_sources(self):
        for source_index in range(num_sources):
            self.add_source(source_index, [-0.75 + 0.25 * source_index, -0.5, 0.0], source_colours[source_index])

    def stop(self):
        if not self.is_running:
            return
        self.osc_server.shutdown()
        self.graph.stop()
        self.is_running = False

    def scale_normalised_x_to_position(self, value: float):
        """
        Scale a normalised [0..1] value to an X position in the environment.
        Args:
            value: A normalised value in the range [0..1]

        Returns:
            The X coordinate, in metres
        """
        environment_diameter_x = (environment_radius_x * 2)
        return (value * environment_diameter_x) - environment_radius_x

    def scale_normalised_y_to_position(self, value: float):
        """
        Scale a normalised [0..1] value to a Y position in the environment.
        Args:
            value: A normalised value in the range [0..1]

        Returns:
            The Y coordinate, in metres
        """
        environment_diameter_y = (environment_radius_y * 2)
        return (value * environment_diameter_y) - environment_radius_y

    def scale_normalised_z_to_position(self, value: float):
        """
        Scale a normalised [0..1] value to a Z position in the environment.
        Args:
            value: A normalised value in the range [0..1]

        Returns:
            The Z coordinate, in metres
        """
        environment_diameter_z = (environment_radius_z * 2)
        return (value * environment_diameter_z) - environment_radius_z

    def handle_midi_message(self, msg):
        """
        MIDI control changes:
          0 = x
          1 = y
          2 = z
          3 = xsin-amp
          4 = xsin-freq
          5 = ysin-amp
          6 = ysin-freq

        Args:
            msg:

        Returns:

        """
        logger.debug("MIDI message: %s" % msg)
        if msg.type == "control_change":
            source_index = msg.channel
            control_index = msg.control - 1
            value = msg.value / 127.0
            logger.debug("[MIDI] Control change: %d %d %f" % (source_index, control_index, value))

            source = self.sources[source_index]
            if control_index in [0, 1, 2]:
                # TODO - rewrite this to not access private _position
                position = source._position
                if control_index == 0:
                    position[0] = self.scale_normalised_x_to_position(value)
                elif control_index == 1:
                    position[1] = self.scale_normalised_y_to_position(value)
                elif control_index == 2:
                    position[2] = self.scale_normalised_z_to_position(value)
                source._position = position
            elif control_index == 3:
                source.xsin_amp = value
            elif control_index == 4:
                source.xsin_freq = scale_lin_exp(value, 0, 1, 0.01, 10.0)
            elif control_index == 5:
                source.ysin_amp = value
            elif control_index == 6:
                source.ysin_freq = scale_lin_exp(value, 0, 1, 0.01, 10.0)

            source.update_visualisation()
            source.update_panner()

    def handle_osc_set_source_position(self, address, *args):
        # address format: /source/*/xyz
        address_parts = address.split("/")
        source_index = int(address_parts[2]) - 1
        x, y, z = args
        logger.debug("Set source %d position: %s %s %s" % (source_index, x, y, z))
        self.sources[source_index].position = [x, y, z]
        self.sources[source_index].update_panner()

    def handle_osc(self, address, *args):
        logger.warning("OSC address not handled: %s (%s)" % (address, args))

    def run_sound_check(self):
        source = WhiteNoise() * 0.02
        clock = Impulse(4)
        source = source * ASREnvelope(0.0, 0, 0.1, clock=clock)
        counter = Counter(clock, 0, self.num_speakers)
        panner = ChannelPanner(self.num_speakers, input=source, pan=counter)
        panner.play()

    def tick(self):
        input_buffer = self.input_channels.output_buffer[0]
        input_buffer_rms = np.sqrt(np.mean(np.square(input_buffer)))
        if input_buffer_rms == 0:
            logger.info("Input RMS: 0")
        else:
            input_buffer_rms_db = 20.0 * np.log10(input_buffer_rms)
            logger.info("Input RMS: %.2fdB" % input_buffer_rms_db)
