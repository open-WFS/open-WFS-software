import numpy as np

class Cuboid:
    """
    A class to represent a 3D cuboid with position, dimensions, and rotation.
    """
    
    def __init__(self,
                 position,
                 dimensions,
                 rotation_angles=(0, 0, 0),
                 color='blue',
                 alpha=0.7):
        """
        Initialize a cuboid.
        
        Args:
            position: (x, y, z) center position
            dimensions: (width, height, depth) dimensions
            rotation_angles: (rx, ry, rz) rotation angles in degrees
            color: color of the cuboid
            alpha: transparency level
        """
        self.position = np.array(position)
        self.dimensions = np.array(dimensions)
        self.rotation_angles = np.array(rotation_angles)
        self.color = color
        self.alpha = alpha
    
    def get_vertices(self):
        """Get the 8 vertices of the cuboid."""
        # Create base cuboid vertices centered at origin
        w, h, d = self.dimensions / 2
        vertices = np.array([
            [-w, -h, -d],  # 0: front-bottom-left
            [+w, -h, -d],  # 1: front-bottom-right
            [+w, +h, -d],  # 2: front-top-right
            [-w, +h, -d],  # 3: front-top-left
            [-w, -h, +d],  # 4: back-bottom-left
            [+w, -h, +d],  # 5: back-bottom-right
            [+w, +h, +d],  # 6: back-top-right
            [-w, +h, +d],  # 7: back-top-left
        ])
        
        # Apply rotations
        vertices = self._rotate_vertices(vertices)
        
        # Translate to final position
        vertices += self.position
        
        return vertices
    
    def get_front_vertices(self):
        """Get the 4 front face vertices of the cuboid."""
        vertices = self.get_vertices()
        return list(vertices)[:4]  # Front face vertices are the first 4
    
    def _rotate_vertices(self, vertices):
        """Apply rotation transformations to vertices."""
        rx, ry, rz = self.rotation_angles
        
        # Rotation matrices
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(rx), -np.sin(rx)],
            [0, np.sin(rx), np.cos(rx)]
        ])
        
        Ry = np.array([
            [np.cos(ry), 0, np.sin(ry)],
            [0, 1, 0],
            [-np.sin(ry), 0, np.cos(ry)]
        ])
        
        Rz = np.array([
            [np.cos(rz), -np.sin(rz), 0],
            [np.sin(rz), np.cos(rz), 0],
            [0, 0, 1]
        ])
        
        # Apply rotations in order: Rz * Ry * Rx
        R = Rz @ Ry @ Rx
        
        return vertices @ R.T
    
    def get_faces(self):
        """Get the 6 faces of the cuboid as lists of vertex indices."""
        return [
            [0, 1, 2, 3],  # front face
            [4, 7, 6, 5],  # back face
            [0, 4, 5, 1],  # bottom face
            [2, 6, 7, 3],  # top face
            [0, 3, 7, 4],  # left face
            [1, 5, 6, 2],  # right face
        ]