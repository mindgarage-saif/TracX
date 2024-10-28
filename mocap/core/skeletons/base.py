from typing import List, Set, Tuple

import numpy as np


def get_range(vals, iqr_factor=2.5):
    """Get the minimum and maximum values of a list of values, ignoring outliers.

    Returns:
        tuple(float, float): Minimum and maximum values.
    """
    # Calculate the IQR to filter out outliers
    q1 = np.percentile(vals, 30)
    q3 = np.percentile(vals, 70)
    iqr = q3 - q1
    lower_bound = q1 - iqr_factor * iqr
    upper_bound = q3 + iqr_factor * iqr

    # Filter out the outliers
    bounded_vals = [x for x in vals if lower_bound <= x <= upper_bound]

    # Return the minimum and maximum of the filtered X coordinates
    if bounded_vals:
        return min(bounded_vals), max(bounded_vals)
    else:
        # In case all points are filtered out, return the min and max of the original data
        return min(vals), max(vals)


class Joint:
    """Class representing a joint in a skeleton.

    Attributes:
        name (str): Name of the joint.
        position (Tuple[float, float, float]): Position of the joint in 3D space.
        rotation (Tuple[float, float, float]): Rotation of the joint in 3D space.
    """

    def __init__(self, name):
        self.name = name
        self._position = (0, 0, 0)
        self._rotation = (0, 0, 0)

    @property
    def position(self):
        return self._position

    @property
    def rotation(self):
        return self._rotation

    def set_position(self, x, y, z):
        """Set the position of the joint.

        Args:
            x (float): X coordinate.
            y (float): Y coordinate.
            z (float): Z coordinate.
        """
        self._position = (x, y, z)

    def set_rotation(self, pitch, yaw, roll):
        """Set the rotation of the joint.

        Args:
            pitch (float): Pitch angle.
            yaw (float): Yaw angle.
            roll (float): Roll angle.
        """
        self._rotation = (pitch, yaw, roll)


class BaseSkeleton:
    """Base class for skeletons.

    Args:
        joint_names (Set[str]): Set of joint names.
        connections (List[Tuple[str, str]]): List of connections between joints.

    Attributes:
        joints (List[Joint]): List of joints in the skeleton.
        feet_joints (List[str]): List of joints that represent feet (used for rendering).
        connections (List[Tuple[int, int]]): List of connections between joints.
    """

    def __init__(self, joint_names: Set[str], connections: List[Tuple[str, str]]):
        self.joints = [Joint(name) for name in joint_names]
        self.feet_joints = []
        self.connections = []
        for i,connection in enumerate(connections):
            joint1 = self.get_joint(connection[0])
            joint2 = self.get_joint(connection[1])
            if not joint1 or not joint2:
                raise ValueError(f"Invalid connection: {connection}")
            self.connections.append((joint1, joint2))

    def set_feet_joints(self, feet_joints: List[str]):
        """Set the joints that represent feet.

        Args:
            feet_joints (List[str]): List of joint names.
        """
        for joint_name in set(feet_joints):
            if not self.get_joint(joint_name):
                raise ValueError(f"Invalid joint name: {joint_name}")

            self.feet_joints.append(joint_name)

    def get_joint(self, name):
        """Get a joint by name.

        Args:
            name (str): Name of the joint to get.

        Returns:
            Joint: The joint with the given name.
        """
        for joint in self.joints:
            if joint.name == name:
                return joint
        return None

    def get_joint_names(self):
        """Get the names of all joints.

        Returns:
            Set[str]: Set of joint names.
        """
        return {joint.name for joint in self.joints}

    def set_joint_position(self, name, x, y, z):
        """Set the position of a joint.

        Args:
            name (str): Name of the joint.
            x (float): X coordinate.
            y (float): Y coordinate.
            z (float): Z coordinate.
        """
        joint = self.get_joint(name)
        if not self.get_joint(name):
            raise ValueError(f"Joint with name {name} does not exist.")

        joint.set_position(x, y, z)

    def set_joint_rotation(self, name, pitch, yaw, roll):
        """Set the rotation of a joint.

        Args:
            name (str): Name of the joint.
            pitch (float): Pitch angle.
            yaw (float): Yaw angle.
            roll (float): Roll angle.
        """
        joint = self.get_joint(name)
        if not self.get_joint(name):
            raise ValueError(f"Joint with name {name} does not exist.")

        joint.set_rotation(pitch, yaw, roll)

    def set_pose(self, pose):
        """Set the pose of the skeleton.

        Args:
            pose (Dict[str, Tuple[float, float, float]]): Dictionary of joint names to positions.
        """
        for name, (x, y, z) in pose.items():
            self.set_joint_position(name, x, y, z)

    def set_rotations(self, rotations):
        """Set the rotations of the skeleton.

        Args:
            rotations (Dict[str, Tuple[float, float, float]]): Dictionary of joint names to rotations.
        """
        for name, (pitch, yaw, roll) in rotations.items():
            self.set_joint_rotation(name, pitch, yaw, roll)

    def get_pose(self):
        """Get the pose of the skeleton.

        Returns:
            Dict[str, Tuple[float, float, float]]: Dictionary of joint names to positions.
        """
        return {joint.name: joint._position for joint in self.joints}

    def get_rotations(self):
        """Get the rotations of the skeleton.

        Returns:
            Dict[str, Tuple[float, float, float]]: Dictionary of joint names to rotations.
        """
        return {joint.name: joint._rotation for joint in self.joints}

    @property
    def x_range(self):
        """Get the minimum and maximum X coordinates of all joints, ignoring outliers.

        Returns:
            tuple(float, float): Minimum and maximum X coordinates.
        """
        return get_range([joint.position[0] for joint in self.joints])

    @property
    def y_range(self):
        """Get the minimum and maximum Y coordinates of all joints, ignoring outliers.

        Returns:
            tuple(float, float): Minimum and maximum Y coordinates.
        """
        return get_range([joint.position[1] for joint in self.joints])

    @property
    def z_range(self):
        """Get the minimum and maximum Z coordinates of all joints, ignoring outliers.

        Returns:
            tuple(float, float): Minimum and maximum Z coordinates.
        """
        return get_range([joint.position[2] for joint in self.joints])
