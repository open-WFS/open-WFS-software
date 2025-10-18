import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def render_cuboids_3d(cuboids,
                      title="3D Cuboids Viewer",
                      xlim=None,
                      ylim=None,
                      zlim=None):
    """
    Render cuboids in an interactive 3D matplotlib plot
    """
    fig = plt.figure(figsize=(12, 10), dpi=72)
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot each cuboid
    for i, cuboid in enumerate(cuboids):
        vertices = cuboid.get_vertices()
        faces = cuboid.get_faces()
        
        # Create face polygons
        face_polygons = []
        for face in faces:
            face_vertices = vertices[face]
            face_polygons.append(face_vertices)
        
        # Add the cuboid as a collection of polygons
        poly3d = Poly3DCollection(face_polygons, 
                                  facecolors=cuboid.color, 
                                  alpha=cuboid.alpha,
                                  edgecolors='black',
                                  linewidths=0.5)
        ax.add_collection3d(poly3d)
        
        # Add a label at the cuboid center
        ax.text(cuboid.position[0], cuboid.position[1], cuboid.position[2], 
                f'C{i+1}', fontsize=8, weight='bold')
    
    # Set up the plot
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)

    
    # Set equal aspect ratio and appropriate limits
    all_vertices = np.vstack([cuboid.get_vertices() for cuboid in cuboids])
    max_range = np.array([all_vertices[:, 0].max() - all_vertices[:, 0].min(),
                         all_vertices[:, 1].max() - all_vertices[:, 1].min(),
                         all_vertices[:, 2].max() - all_vertices[:, 2].min()]).max() / 2.0
    
    mid_x = (all_vertices[:, 0].max() + all_vertices[:, 0].min()) * 0.5
    mid_y = (all_vertices[:, 1].max() + all_vertices[:, 1].min()) * 0.5
    mid_z = (all_vertices[:, 2].max() + all_vertices[:, 2].min()) * 0.5
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(0, mid_z + max_range)
    
    # plt.tight_layout()
    
    return fig, ax