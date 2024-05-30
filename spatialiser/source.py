import random
import logging
import numpy as np
from signalflow import *
from pythonosc.udp_client import SimpleUDPClient
from .constants import input_device_name, output_device_name, num_speakers, input_buffer_size, output_buffer_size
from .constants import module_layout, num_sources, num_speakers_per_module, disable_lfe
from .constants import environment_radius_x, environment_radius_y, environment_radius_z, source_colours, disable_midi
from .constants import crossover_frequency
from .dust import start_dust_process

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
        self.x.input = position[0]
        self.y.input = position[1]
        self.z.input = position[2]

