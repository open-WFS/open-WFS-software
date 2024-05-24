import time
import threading
import pandas as pd
from signalflow import *
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from .constants import input_device_name, output_device_name, num_speakers, input_buffer_size, output_buffer_size

class Spatialiser:
    def __init__(self, osc_port: int = 9130, show_cpu: bool = False):
        """

        Args:
             osc_port: The port to listen for OSC messages on. Default is 9130, which is the port used by the
                       source-viewer node application.
        """
        config = AudioGraphConfig()
        config.input_device_name = input_device_name
        config.output_device_name = output_device_name
        config.input_buffer_size = input_buffer_size
        config.output_buffer_size = output_buffer_size
        self.graph = AudioGraph(config=config, start=False)
        if show_cpu:
            self.graph.poll(1)
        self.is_running = False

        # create an OSC server
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self.handle_osc)
        self.osc_server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", osc_port),
                                                           dispatcher)

        self.visualiser = SimpleUDPClient("127.0.0.1", 9129)
        self.visualiser.send_message("/grid/xy/on", [1])
        time.sleep(0.1)
        self.visualiser.send_message("/grid/size", [4])
        self.visualiser.send_message("/grid/section/size", [1])
        self.visualiser.send_message("/grid/subdiv/num", [10])
        time.sleep(0.1)

        self.visualiser.send_message("/source/number", [4])
        time.sleep(0.1)
        self.visualiser.send_message("/source/size", [30.0])
        self.visualiser.send_message("/source/1/color", [1.0, 0.0, 0.0, 1.0])
        self.visualiser.send_message("/source/2/color", [0.0, 1.0, 0.0, 1.0])
        self.visualiser.send_message("/source/3/color", [0.0, 0.0, 1.0, 1.0])
        self.visualiser.send_message("/source/4/color", [0.0, 1.0, 1.0, 1.0])
        self.visualiser.send_message("/source/1/xyz", [-0.5, 0.1, 0.1])
        self.visualiser.send_message("/source/2/xyz", [0, 0.1, 0.1])
        self.visualiser.send_message("/source/3/xyz", [0.5, 0.1, 0.1])
        self.visualiser.send_message("/source/4/xyz", [1.0, 0.1, 0.1])

        speaker_layout = pd.read_csv("../../Data/allspeaker_pos_v2.csv")
        self.env = SpatialEnvironment()
        self.num_speakers = num_speakers

        self.visualiser.send_message("/speaker/number", [num_speakers])
        time.sleep(0.1)
        self.visualiser.send_message("/speaker/size", [30.0])

        time.sleep(0.1)
        # TODO: source-viewer bug: Need to sleep between /speaker/number and /speaker/1/xyz
        # TODO: source-viewer bug: /size is not documented
        for row_index, speaker in list(speaker_layout.iterrows())[:self.num_speakers]:
            speaker_x = speaker.x * 0.001
            speaker_y = speaker.y * 0.001
            print("Added speaker: %.4f, %.4f" % (speaker_x, speaker_y))
            self.env.add_speaker(row_index, speaker_x, 0.5, speaker_y)
            speaker_index = row_index + 1
            self.visualiser.send_message("/speaker/%d/xyz" % speaker_index, [speaker_x, 0.5, speaker_y])



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

    def add_sources(self):
        # source = WhiteNoise() * 0.002
        channels = AudioIn(4) * 0.1
        # channels = SineOscillator([440, 660, 880, 1080]) * 0.002

        self.panner1 = SpatialPanner(env=self.env, input=channels[0], x=Smooth(-0.5, 0.999),
                                    y=0.5, z=0.1,
                                    algorithm="dbap", radius=0.25, use_delays=True)
        self.panner1.play()

        self.panner2 = SpatialPanner(env=self.env, input=channels[1], x=Smooth(0.0, 0.999),
                                    y=0.5, z=0.1,
                                    algorithm="dbap", radius=0.25, use_delays=True)
        self.panner2.play()

        self.panner3 = SpatialPanner(env=self.env, input=channels[2], x=Smooth(0.5, 0.999),
                                    y=0.5, z=0.1,
                                    algorithm="dbap", radius=0.25, use_delays=True)
        self.panner3.play()

        self.panner4 = SpatialPanner(env=self.env, input=channels[3], x=Smooth(1.0, 0.999),
                                    y=0.5, z=0.1,
                                    algorithm="dbap", radius=0.25, use_delays=True)
        self.panner4.play()

        # source.play()

    def stop(self):
        if not self.is_running:
            return
        self.osc_server.shutdown()
        self.graph.stop()
        self.is_running = False

    def handle_osc(self, address, *args):
        if address == "/source/1/xyz":
            x, y, z = args
            print("Source 1 position: %s %s %s" % (x, y, z))
            self.panner1.x.input = x
        elif address == "/source/2/xyz":
            x, y, z = args
            print("Source 2 position: %s %s %s" % (x, y, z))
            self.panner2.x.input = x
        elif address == "/source/3/xyz":
            x, y, z = args
            print("Source 3 position: %s %s %s" % (x, y, z))
            self.panner3.x.input = x
        elif address == "/source/4/xyz":
            x, y, z = args
            print("Source 4 position: %s %s %s" % (x, y, z))
            self.panner4.x.input = x

    def run_sound_check(self):
        source = WhiteNoise() * 0.02
        clock = Impulse(4)
        source = source * ASREnvelope(0.0, 0, 0.1, clock=clock)
        counter = Counter(clock, 0, self.num_speakers)
        panner = ChannelPanner(self.num_speakers, input=source, pan=counter)
        panner.play()
