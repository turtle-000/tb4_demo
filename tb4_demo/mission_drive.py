#!/usr/bin/env python3
import time
from geometry_msgs.msg import TwistStamped
import rclpy
from rclpy.node import Node


class MissionDriver(Node):

  def __init__(self):
    super().__init__('mission_drive')
    self.publisher_ = self.create_publisher(TwistStamped, '/cmd_vel', 10)
    self.get_logger().info('Mission Drive Node Started!')

  def publish_cmd(self, linear_x: float, angular_z: float, duration: float):
    start_time = self.get_clock().now()
    while (self.get_clock().now() - start_time).nanoseconds / 1e9 < duration:
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

  # 【演習課題用パラメータ設定欄】
  # 課題条件（d = v * t, θ = ω * t）に基づいて適切な値を計算・変更すること
  FORWARD_SPEED_1 = 0.1  # 往路速度 [m/s]
  FORWARD_TIME_1 = 2.0  # 往路時間 [s]

  ROTATE_SPEED = 0.2  # 旋回速度 [rad/s]
  ROTATE_TIME = 1.0  # 旋回時間 [s]

  FORWARD_SPEED_2 = 0.1  # 復路速度 [m/s]
  FORWARD_TIME_2 = 2.0  # 復路時間 [s]

  try:
    node.get_logger().info('--- Mission Start ---')
    time.sleep(1.0)
    node.publish_cmd(
        linear_x=FORWARD_SPEED_1, angular_z=0.0, duration=FORWARD_TIME_1
    )
    node.publish_cmd(
        linear_x=0.0, angular_z=ROTATE_SPEED, duration=ROTATE_TIME
    )
    node.publish_cmd(
        linear_x=FORWARD_SPEED_2, angular_z=0.0, duration=FORWARD_TIME_2
    )
    node.get_logger().info('--- Mission Complete! ---')
  except KeyboardInterrupt:
    node.stop()
  finally:
    node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()


if __name__ == '__main__':
  main()