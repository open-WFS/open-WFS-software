import numpy as np
from signalflow import Node, SpatialEnvironment, SpatialPanner, Clip, Smooth

class Source:
    def __init__(self,
                 index: int,
                 environment: SpatialEnvironment,
                 audio: Node,
                 position: np.ndarray = None):
        self.index = index
        self.environment = environment
        self.audio = audio

        # from signalflow import WhiteNoise
        # self.audio = WhiteNoise() * 0.2

        self._radius = 0.25
        self._position = position
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
                                    algorithm="dbap",
                                    radius=self.radius_smoothed)
        
        self.limiter = Clip(self.panner, min=-0.5, max=0.5)
        self.limiter.play()
    
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