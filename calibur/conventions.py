import numpy

class CameraConventions:
    """
    Conventions of camera coordinate systems in right, up, forward order.
    Also available as CC for faster typing.
    """
    GL = ("X", "Y", "-Z")
    Godot = Blender = OpenGL = GL
    CV = ("X", "-Y", "Z")
    OpenCV = CV
    ROS = ("-Y", "Z", "X")
    DirectXLH = ("X", "Y", "Z")
    Unity = DirectXLH
    UE = ("Y", "Z", "X")

class WorldConventions:
    """
    Conventions of world coordinate systems in right, up, forward order.
    Currently experimental, as the definition of world forward is tricky.
    The up axis is in general accurate and not ambiguous.
    """
    Blender = ("X", "Z", "Y")
    GL = ("X", "Y", "Z")  # TODO: double check
    GLTF = Godot = Unity = DirectXLH = GL
    ROS = CameraConventions.ROS
    UE = ("-X", "Z", "Y")


CC = CameraConventions


axes = {
    "X": [1, 0, 0],
    "-X": [-1, 0, 0],
    "Y": [0, 1, 0],
    "-Y": [0, -1, 0],
    "Z": [0, 0, 1],
    "-Z": [0, 0, -1]
}


def get_ruf_basis(convention):
    r, u, f = convention
    r, u, f = axes[r], axes[u], axes[f]
    return numpy.stack([r, u, f], axis=-1).astype(numpy.float32)


def convert_pose(src_pose, src_convention, dst_convention):
    """
    Converts a pose [..., 4, 4].
    Think of a pose as:
        A small object has a fixed relative position to the camera.
        The camera pose transforms the relative position into a world position.
        A @ p_c = p_w
    The conversion works as:
        We have a camera with pose A in system A (say OpenGL).
        Now we instead want a camera in system B (say OpenCV) to see the same scene.
        What should be its pose?
        We want to transform a point with same 'right, up and forward' relative to the camera
        into the same world point.
        The answer would be `convert_pose(A, CC.GL, CC.CV)`.
    The algorithm:
        Given p_w = p_w', p_c dot r/u/f = p_c' dot r'/u'/f'
        or p_c^T [r|u|f] = p_c'^T [r'|u'|f'].
        p_c^T = p_c'^T [r'|u'|f'] [r|u|f]^(-1).
        A @ p_c = B @ p_c'
        = A @ [r|u|f]^(-1)^T @ [r'|u'|f']^T @ p_c'
        Thus B = A @ [r|u|f]^(-1)^T @ [r'|u'|f']^T .
        For homogeneous coordinates, we simply pad [r|u|f] with [0 0 0 1]
        and the transform would be the same as [r|u|f] matmul on p_c'.
    """
    basis_a = get_ruf_basis(src_convention)
    basis_b = get_ruf_basis(dst_convention)
    transform = numpy.eye(4, dtype=basis_a.dtype)
    transform[:3, :3] = basis_a @ basis_b.T
    return src_pose @ transform
