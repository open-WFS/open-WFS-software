import numpy as np
from signalflow import *

class Source:
    def __init__(self,
                 index: int,
                 environment: SpatialEnvironment,
                 audio: Node,
                 output_bus: Bus,
                 position: np.ndarray = None):
        self.index = index
        self.environment = environment
        self.audio = audio
        self.output_bus = output_bus

        self._radius = 2.5
        self._position = position
        self._algorithm = "beamformer"
        if self._position is None:
            self._position = np.array([0, 0, 0])

        self.x_smoothed = Smooth(self._position[0], 0.999)
        self.y_smoothed = Smooth(self._position[1], 0.999)
        self.z_smoothed = Smooth(self._position[2], 0.999)
        self.radius_smoothed = Smooth(self._radius, 0.999)

        self.panner = SpatialPanner(env=environment,
                                    input=self.audio,
                                    x=self.x_smoothed,
                                    y=self.y_smoothed,
                                    z=self.z_smoothed,
                                    algorithm=self._algorithm,
                                    radius=self.radius_smoothed)
    
        self.is_muted = False
        self.is_soloed = False
        
        # self.delayed = ChannelArray([CombDelay(self.panner[n], feedback=0.95, delay_time=random.uniform(0.01, 0.05)) for n in range(num_channels)])
        self.output_bus.add_input(self.panner)
    
    def get_position(self):
        return self._position

    def set_position(self, position):
        self._position = position
        self.x_smoothed.input = position[0]
        self.y_smoothed.input = position[1]
        self.z_smoothed.input = position[2]

    position = property(get_position, set_position)

    def get_radius(self):
        return self._radius
    
    def set_radius(self, radius):
        self._radius = radius
        self.radius_smoothed.input = radius
    
    radius = property(get_radius, set_radius)

    def get_algorithm(self):
        return self.panner.algorithm

    def set_algorithm(self, algorithm):
        self.panner.set_property("algorithm", algorithm)

    algorithm = property(get_algorithm, set_algorithm)