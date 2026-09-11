#!/usr/bin/env python3
import time
from geometry_msgs.msg import TwistStamped
import rclpy
from rclpy.node import Node


class SimpleDriver(Node):

  def __init__(self):
    super().__init__('drive_simple')
    self.publisher_ = self.create_publisher(TwistStamped, '/cmd_vel', 10)
    self.get_logger().info('Drive Simple Node started.')

  def drive_forward(self, speed: float, duration: float):
    self.get_logger().info(
        f'Moving forward: speed={speed} m/s for {duration} seconds...'
    )
    start_time = self.get_clock().now()
    while (self.get_clock().now() - start_time).nanoseconds / 1e9 < duration:
      msg = TwistStamped()
      msg.header.stamp = self.get_clock().now().to_msg()
      msg.twist.linear.x = speed
      msg.twist.angular.z = 0.0
      self.publisher_.publish(msg)
      time.sleep(0.1)
    self.stop()

  def stop(self):
    msg = TwistStamped()
    msg.header.stamp = self.get_clock().now().to_msg()
    msg.twist.linear.x = 0.0
    msg.twist.angular.z = 0.0
    self.publisher_.publish(msg)
    self.get_logger().info('Robot stopped.')


def main(args=None):
  rclpy.init(args=args)
  node = SimpleDriver()
  try:
    time.sleep(1.0)
    node.drive_forward(speed=0.15, duration=7.0)
  except KeyboardInterrupt:
    node.stop()
  finally:
    node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()


if __name__ == '__main__':
  main()