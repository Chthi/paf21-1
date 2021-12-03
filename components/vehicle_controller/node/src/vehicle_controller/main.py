#!/usr/bin/env python
"""Main script defining the ROS node"""

from dataclasses import dataclass
import rospy
from ackermann_msgs.msg import AckermannDrive
from std_msgs.msg import String as StringMsg, Float32 as FloatMsg
from sensor_msgs.msg import NavSatFix as GpsMsg

from vehicle_controller.driving import SimpleDrivingSignalConverter


@dataclass
class VehicleControllerNode:
    """A class representing a ROS node that's capable of controlling a vehicle
    and make it drive according to a given route the node is constantly receiving."""

    vehicle_name: str
    publish_rate_in_hz: float
    signal_converter = SimpleDrivingSignalConverter()
    driving_signal_publisher: rospy.Publisher = None

    def run_node(self):
        """Launch the ROS node to receive planned routes
        and convert them into AckermannDrive signals"""
        self._init_ros()
        rate = rospy.Rate(self.publish_rate_in_hz)

        while not rospy.is_shutdown():
            signal = self.signal_converter.next_signal()
            self.driving_signal_publisher.publish(signal)
            rate.sleep()

    def _init_ros(self):
        rospy.init_node(f'test_simple_driving_{self.vehicle_name}', anonymous=True)
        self.driving_signal_publisher = self._init_driving_signal_publisher()
        self._init_route_subscriber()
        self._init_target_velocity_subscriber()
        self._init_gps_subscriber()

    def _init_route_subscriber(self):
        in_topic = f"/drive/{self.vehicle_name}/local_route"
        rospy.Subscriber(in_topic, StringMsg, self.signal_converter.update_route)

    def _init_target_velocity_subscriber(self):
        in_topic = f"/drive/{self.vehicle_name}/target_velocity"
        rospy.Subscriber(in_topic, FloatMsg, self.signal_converter.update_target_velocity)

    def _init_gps_subscriber(self):
        in_topic = f"/carla/{self.vehicle_name}/gnss/gnss1/fix"
        rospy.Subscriber(in_topic, GpsMsg, self.signal_converter.update_vehicle_position)

    def _init_driving_signal_publisher(self):
        out_topic = f"/carla/{self.vehicle_name}/ackermann_cmd"
        return rospy.Publisher(out_topic, AckermannDrive, queue_size=100)


def main():
    """The main entrypoint launching the ROS node
    with specific configuration parameters"""
    vehicle_name = "ego_vehicle"
    publish_rate_hz = 10
    input_topics = []

    node = VehicleControllerNode(vehicle_name, publish_rate_hz, input_topics)
    node.run_node()


if __name__ == '__main__':
    main()
