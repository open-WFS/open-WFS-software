import time
import mido
import logging
import threading
import numpy as np
import pandas as pd
from signalflow import *
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from .constants import input_device_name, output_device_name, num_speakers, input_buffer_size, output_buffer_size
from .constants import module_layout

logger = logging.getLogger(__name__)

class SpatialSource:
    def __init__(self,
                 index: int,
                 position: list[float],
                 visualiser: SimpleUDPClient):
        self.index = index
        self.index_1indexed = self.index + 1
        self.panner = None
        self.index = index
        self._position = position
        self.visualiser = visualiser

    def get_position(self):
        return self._position
    def set_position(self, position):
        print("set_position: %s" % position)
        self._position = position
    position = property(get_position, set_position)

    def update_visualisation(self):
        print("updating vis: %s" % self._position)
        self.visualiser.send_message("/source/%d/xyz" % self.index_1indexed, self._position)

    def update_panner(self):
        self.panner.x.input = self._position[0]
        self.panner.y.input = self._position[1]
        self.panner.z.input = self._position[2]

class SpatialSpeaker:
    pass

class Spatialiser:
    def __init__(self, osc_port: int = 9130, show_cpu: bool = False):
        """
        Args:
            osc_port: The port to listen for OSC messages on. Default is 9130, which is the port used by the
                       source-viewer node application.
            show_cpu: If True, show CPU usage in the console.
        """
        config = AudioGraphConfig()
        config.input_device_name = input_device_name
        config.output_device_name = output_device_name
        config.input_buffer_size = input_buffer_size
        config.output_buffer_size = output_buffer_size
        self.graph = AudioGraph(config=config, start=False)
        self.input_channels = AudioIn(4) * 0.000000001
        if show_cpu:
            self.graph.poll(1)
        self.is_running = False

        # create an OSC server
        dispatcher = Dispatcher()
        dispatcher.map("/source/*/xyz", self.handle_osc_set_source_position)
        dispatcher.set_default_handler(self.handle_osc)
        self.osc_server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", osc_port),
                                                           dispatcher)

        # Start listening for MIDI events
        inport = mido.open_input(name="IAC Driver Bus 1")
        inport.callback = self.handle_midi_message

        #--------------------------------------------------------------------------------
        # Visualiser: General setup
        #--------------------------------------------------------------------------------
        self.visualiser = SimpleUDPClient("127.0.0.1", 9129)
        self.visualiser.send_message("/source/fade", [0])
        self.visualiser.send_message("/grid/xy/on", [1])
        time.sleep(0.1)
        self.visualiser.send_message("/grid/size", [4])
        self.visualiser.send_message("/grid/section/size", [1])
        self.visualiser.send_message("/grid/subdiv/num", [10])
        time.sleep(0.1)
        self.visualiser.send_message("/source/size", [30.0])

        #--------------------------------------------------------------------------------
        # Audio: Add speakers
        #--------------------------------------------------------------------------------
        self.speakers = []
        self.num_speakers = num_speakers
        self.env = SpatialEnvironment()

        self.visualiser.send_message("/speaker/number", [num_speakers])
        time.sleep(0.1)
        self.visualiser.send_message("/speaker/size", [30.0])
        time.sleep(0.1)

        speaker_layout = pd.read_csv("../../Data/allspeaker_pos_v2.csv")
        for module in module_layout:
            for row_index, speaker in list(speaker_layout.iterrows())[:self.num_speakers]:
                module_speaker_x = module.position[0] + np.cos(module.rotation) * (speaker.x * 0.001)
                module_speaker_y = module.position[1] + np.sin(module.rotation) * (speaker.x * 0.001)
                module_speaker_z = module.position[2] + speaker.y * 0.001
                self.add_speaker([module_speaker_x,
                                  module_speaker_y,
                                  module_speaker_z])

        #--------------------------------------------------------------------------------
        # Audio: Add sources
        #--------------------------------------------------------------------------------
        self.sources = []
        self.add_sources()

    def run(self):
        self.osc_server.serve_forever()

    def start(self):
        if self.is_running:
            return
        self.graph.start()
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        self.is_running = True

    def add_speaker(self, position: list):
        index = len(self.speakers)
        logger.debug("Added speaker %d: %s" % (index, position))
        self.env.add_speaker(index, *position)
        self.visualiser.send_message("/speaker/%d/xyz" % (index + 1), position)
        speaker = SpatialSpeaker()
        self.speakers.append(speaker)

    def add_source(self, position: list, color: list):
        logger.info("Add source: %s" % position)
        index = len(self.sources)
        index_1indexed = index + 1

        self.visualiser.send_message("/source/number", [index_1indexed])
        time.sleep(0.1)
        self.visualiser.send_message("/source/%d/color" % index_1indexed, color)

        source = SpatialSource(index, position, self.visualiser)
        # self.visualiser.send_message("/source/%d/xyz" % index_1indexed, position)
        source.update_visualisation()
        self.sources.append(source)

        source.panner = SpatialPanner(env=self.env,
                                      input=self.input_channels[index],
                                      x=Smooth(position[0], 0.999),
                                      y=Smooth(position[1], 0.999),
                                      z=Smooth(position[2], 0.999),
                                      algorithm="beamformer",
                                      radius=0.5,
                                      use_delays=True)
        source.panner.play()

    def add_sources(self):
        self.add_source([0.0, -1.0, 0.1], [1.0, 0.0, 0.0, 1.0])
        self.add_source([0.5, -1.0, 0.1], [0.0, 1.0, 0.0, 1.0])
        self.add_source([1.0, -1.0, 0.1], [0.0, 0.0, 1.0, 1.0])
        self.add_source([0.75, -1.0, 0.1], [0.0, 1.0, 1.0, 1.0])

    def stop(self):
        if not self.is_running:
            return
        self.osc_server.shutdown()
        self.graph.stop()
        self.is_running = False

    def handle_midi_message(self, msg):
        logger.debug("MIDI message: %s" % msg)
        if msg.type == "control_change":
            source_index = msg.channel
            control_index = msg.control - 1
            value = msg.value / 127.0
            logger.info("Control change: %d %d %f" % (source_index, control_index, value))

            if control_index in [0, 1, 2]:
                source = self.sources[source_index]
                value = 5 * value - 2.5
                position = source.position

                if control_index == 0:
                    position[0] = value
                elif control_index == 1:
                    position[1] = value
                elif control_index == 2:
                    position[2] = value

                source.position = position
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
