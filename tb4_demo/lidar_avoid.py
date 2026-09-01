#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data
from rclpy.executors import ExternalShutdownException
import math

class LidarAvoidNode(Node):
    def __init__(self):
        super().__init__('lidar_avoid')
        self.cmd_pub_ = self.create_publisher(TwistStamped, '/cmd_vel', 1)
        self.scan_sub_ = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile_sensor_data
        )
        self.timer_ = self.create_timer(0.1, self.control_loop)

        # 動作・安全パラメータ
        self.STOP_DISTANCE = 0.5     # 壁の手前 0.5m で停止
        self.FORWARD_SPEED = 0.15    # 直進速度 [m/s]
        self.ROTATE_SPEED = 0.5     # 回転速度 [rad/s] (プラス: 左回転)
        
        # 回転補正係数 (床面摩擦に応じて 1.1 〜 1.3 程度で調整)
        self.ROTATE_FACTOR = 1.15
        self.ROTATE_DURATION = (math.pi / self.ROTATE_SPEED) * self.ROTATE_FACTOR

        self.FRONT_IDX = 200
        self.INDEX_RANGE = 30

        self.state_ = 'FORWARD'      # 'FORWARD', 'ROTATING', 'RETURN', 'FINISHED'
        self.front_distance_ = float('inf')
        
        self.forward_start_time_ = None
        self.forward_duration_ = 0.0
        self.rotate_start_time_ = None
        self.return_start_time_ = None

        self.get_logger().info('LiDAR Wall Detection & Return Node Started!')

    def scan_callback(self, msg: LaserScan):
        num_samples = len(msg.ranges)
        if num_samples == 0:
            return

        start_idx = max(0, self.FRONT_IDX - self.INDEX_RANGE)
        end_idx = min(num_samples, self.FRONT_IDX + self.INDEX_RANGE)
        front_ranges = msg.ranges[start_idx:end_idx]
        valid_ranges = [r for r in front_ranges if msg.range_min < r < msg.range_max]

        if valid_ranges:
            self.front_distance_ = min(valid_ranges)
            if self.front_distance_ < 0.8 and self.state_ == 'FORWARD':
                self.get_logger().info(
                    f"【正面検知】最接近距離: {self.front_distance_:.2f}m (IDX: {self.FRONT_IDX}周辺)"
                )
        else:
            self.front_distance_ = float('inf')

    def control_loop(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        now = self.get_clock().now()

        # 【ステート1: 壁まで前進＆時間計測】
        if self.state_ == 'FORWARD':
            if self.forward_start_time_ is None:
                self.forward_start_time_ = now

            if self.front_distance_ < self.STOP_DISTANCE:
                self.forward_duration_ = (now - self.forward_start_time_).nanoseconds / 1e9
                self.get_logger().info(
                    f"壁を検知 ({self.front_distance_:.2f}m)。"
                    f"往路時間: {self.forward_duration_:.2f}秒。180度回転を開始します。"
                )
                self.state_ = 'ROTATING'
                self.rotate_start_time_ = now
                msg.twist.linear.x = 0.0
                msg.twist.angular.z = 0.0
            else:
                msg.twist.linear.x = self.FORWARD_SPEED
                msg.twist.angular.z = 0.0

        # 【ステート2: 180度回転】
        elif self.state_ == 'ROTATING':
            elapsed = (now - self.rotate_start_time_).nanoseconds / 1e9
            if elapsed >= self.ROTATE_DURATION:
                self.get_logger().info(
                    f"回転完了。往路と同じ時間 ({self.forward_duration_:.2f}秒) 復帰直進します。"
                )
                self.state_ = 'RETURN'
                self.return_start_time_ = now
                msg.twist.linear.x = 0.0
                msg.twist.angular.z = 0.0
            else:
                msg.twist.linear.x = 0.0
                msg.twist.angular.z = self.ROTATE_SPEED

        # 【ステート3: 往路と同じ時間だけ復帰直進】
        elif self.state_ == 'RETURN':
            elapsed = (now - self.return_start_time_).nanoseconds / 1e9
            if elapsed >= self.forward_duration_:
                self.get_logger().info("元の位置まで戻りました。プログラムを終了します。")
                self.state_ = 'FINISHED'
                
                msg.twist.linear.x = 0.0
                msg.twist.angular.z = 0.0
                self.cmd_pub_.publish(msg)
                rclpy.shutdown()
                return
            else:
                msg.twist.linear.x = self.FORWARD_SPEED
                msg.twist.angular.z = 0.0

        self.cmd_pub_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = LidarAvoidNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            stop_msg = TwistStamped()
            stop_msg.header.stamp = node.get_clock().now().to_msg()
            node.cmd_pub_.publish(stop_msg)
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()
