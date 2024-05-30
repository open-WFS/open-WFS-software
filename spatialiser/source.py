import random
import logging
import numpy as np
from signalflow import *
from pythonosc.udp_client import SimpleUDPClient
from .constants import input_device_name, output_device_name, num_speakers, input_buffer_size, output_buffer_size
from .constants import module_layout, num_sources, num_speakers_per_module, disable_lfe
from .constants import environment_radius_x, environment_radius_y, environment_radius_z, source_colours, disable_midi
from .constants import crossover_frequency
from multiprocessing import Process, Pipe


logger = logging.getLogger(__name__)


class SpatialSource:
    def __init__(self,
                 index: int,
                 position: list[float],
                 visualiser: SimpleUDPClient):
        self.index = index
        self.index_1indexed = self.index + 1
        self.panner = None
        self.random_panner = None
        self.index = index
        self._position = position
        self.visualiser = visualiser
        self.xsin_amp = random.uniform(0.1, 0.25)
        self.xsin_freq = random.uniform(0.25, 1.0)
        self.xsin_amp = 0
        self.xsin_freq = 0
        self.xphase = 0.0
        self.ysin_amp = random.uniform(0.1, 0.25)
        self.ysin_freq = random.uniform(0.25, 1.0)
        self.ysin_amp = 0
        self.ysin_freq = 0
        self.yphase = 0.0

    def start_audio(self, speaker_positions: list[list]):
        self.parent_conn, self.child_conn = Pipe()
        self.audio_process = Process(target=self.run_panner_process, args=(self.index, self.position, speaker_positions, self.child_conn))
        self.audio_process.start()

    def run_panner_process(self,
                           source_index: int,
                           position: list,
                           speaker_positions: list[list[float]],
                           child_conn):
        config = AudioGraphConfig()
        config.input_device_name = input_device_name
        config.output_device_name = output_device_name
        config.input_buffer_size = input_buffer_size
        config.output_buffer_size = output_buffer_size
        graph = AudioGraph(config=config)

        raw_input_channels = AudioIn(8) * 0.25

        # TODO: Why does BiquadFilter not work here?
        input_channels = SVFilter(input=raw_input_channels,
                                  filter_type="high_pass",
                                  resonance=0.0,
                                  cutoff=crossover_frequency)
        # pan LFE to last channel
        if not disable_lfe:
            mono_mixdown = ChannelMixer(num_channels=1,
                                        input=raw_input_channels)
            lfe_channel = SVFilter(input=mono_mixdown,
                                   filter_type="low_pass",
                                   resonance=0.0,
                                   cutoff=400) * 20
            lfe_panner = ChannelPanner(num_channels=64,
                                       input=lfe_channel,
                                       pan=62)
            lfe_panner.play()

        env = SpatialEnvironment()
        for speaker_index, position in enumerate(speaker_positions):
            env.add_speaker(speaker_index, *position)

        x = Smooth(position[0], 0.999)
        y = Smooth(position[1], 0.999)
        z = Smooth(position[2], 0.999)
        panner = SpatialPanner(env=env,
                               input=input_channels[source_index],
                               x=x,
                               y=y,
                               z=z,
                               algorithm="beamformer",
                               radius=0.5,
                               use_delays=True)

        # TODO: Really want a soft limiter
        limiter = Clip(panner, min=-0.25, max=0.25)
        limiter.play()

        while True:
            position = child_conn.recv()
            x.input = position[0]
            y.input = position[1]
            z.input = position[2]

    def tick(self, delta_seconds: float):
        self.xphase += self.xsin_freq * delta_seconds
        while self.xphase > np.pi * 2:
            self.xphase -= np.pi * 2

        self.yphase += self.ysin_freq * delta_seconds
        while self.yphase > np.pi * 2:
            self.yphase -= np.pi * 2

    def get_position(self):
        return [
            self._position[0] + self.xsin_amp * np.sin(self.xphase * np.pi * 2),
            self._position[1] + self.ysin_amp * np.cos(self.yphase * np.pi * 2),
            self._position[2]
        ]

    def set_position(self, position):
        self._position = position

    position = property(get_position, set_position)

    def update_visualisation(self):
        logger.debug("[Source %02d] Updating visualiser: %s" % (self.index_1indexed, self.position))
        self.visualiser.send_message("/source/%d/xyz" % self.index_1indexed, self.position)

    def update_panner(self):
        position = self.position
        logger.debug("[Source %02d] Updating panner: %s" % (self.index_1indexed, position))
        self.parent_conn.send(position)
