# tb4_demo

ROS 2 (Jazzy) / TurtleBot 4 実習用パッケージです。

## ノード一覧
1. `drive_simple`: 時間制御による直線走行と理論距離の検証
2. `mission_drive`: コース走破用パラメータ書き換え実習
3. `lidar_avoid`: LiDARセンサによる壁検知・180度反転・復帰自動停止制御

## 動作方法
```bash
colcon build --packages-select tb4_demo
source install/setup.bash
ros2 run tb4_demo drive_simple
ros2 run tb4_demo mission_drive
ros2 run tb4_demo lidar_avoid
