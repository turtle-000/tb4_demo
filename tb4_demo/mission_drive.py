#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
import time

class MissionDriver(Node):
    def __init__(self):
        super().__init__('mission_driver')
        self.publisher_ = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.get_logger().info('Mission Driver Node Started!')

    def publish_cmd(self, linear_x: float, angular_z: float, duration: float):
        start_time = time.time()
        while time.time() - start_time < duration:
            msg = TwistStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.twist.linear.x = linear_x
            msg.twist.angular.z = angular_z
            self.publisher_.publish(msg)
            time.sleep(0.1)
        self.stop()
        time.sleep(0.5)

    def stop(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.twist.linear.x = 0.0
        msg.twist.angular.z = 0.0
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MissionDriver()

    # 生徒課題用初期値
    FORWARD_SPEED_1 = 0.1
    FORWARD_TIME_1  = 2.0
    ROTATE_SPEED    = 0.2
    ROTATE_TIME     = 1.0
    FORWARD_SPEED_2 = 0.1
    FORWARD_TIME_2  = 2.0

    try:
        node.get_logger().info('--- Mission Start ---')
        time.sleep(1.0)
        node.publish_cmd(linear_x=FORWARD_SPEED_1, angular_z=0.0, duration=FORWARD_TIME_1)
        node.publish_cmd(linear_x=0.0, angular_z=ROTATE_SPEED, duration=ROTATE_TIME)
        node.publish_cmd(linear_x=FORWARD_SPEED_2, angular_z=0.0, duration=FORWARD_TIME_2)
        node.get_logger().info('--- Mission Complete! ---')
    except KeyboardInterrupt:
        node.stop()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
