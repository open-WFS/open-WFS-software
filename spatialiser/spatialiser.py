import time
import logging
import threading
import pandas as pd
from signalflow import *
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from .constants import input_device_name, output_device_name, num_speakers, input_buffer_size, output_buffer_size

logger = logging.getLogger(__name__)

class SpatialSource:
    def __init__(self):
        self.panner = None

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

        #--------------------------------------------------------------------------------
        # Visualiser: General setup
        #--------------------------------------------------------------------------------
        self.visualiser = SimpleUDPClient("127.0.0.1", 9129)
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
        for row_index, speaker in list(speaker_layout.iterrows())[:self.num_speakers]:
            self.add_speaker([speaker.x * 0.001, 0.0, speaker.y * 0.001])

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
        self.visualiser.send_message("/source/%d/xyz" % index_1indexed, position)

        source = SpatialSource()
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

    def stop(self):
        if not self.is_running:
            return
        self.osc_server.shutdown()
        self.graph.stop()
        self.is_running = False

    def handle_osc_set_source_position(self, address, *args):
        # address format: /source/*/xyz
        address_parts = address.split("/")
        source_index = int(address_parts[2]) - 1
        x, y, z = args
        logger.debug("Set source %d position: %s %s %s" % (source_index, x, y, z))
        self.sources[source_index].panner.x.input = x
        self.sources[source_index].panner.y.input = y
        self.sources[source_index].panner.z.input = z

    def handle_osc(self, address, *args):
        logger.warning("OSC address not handled: %s (%s)" % (address, args))

    def run_sound_check(self):
        source = WhiteNoise() * 0.02
        clock = Impulse(4)
        source = source * ASREnvelope(0.0, 0, 0.1, clock=clock)
        counter = Counter(clock, 0, self.num_speakers)
        panner = ChannelPanner(self.num_speakers, input=source, pan=counter)
        panner.play()
