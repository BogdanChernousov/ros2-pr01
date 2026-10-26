import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class PoseRelay(Node):
    def __init__(self):
        super().__init__('pose_relay')
        self.sub = self.create_subscription(Pose, '/turtle1/pose', self.cb, 10)

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        self.pub = self.create_publisher(Pose, 'sensor_pose', qos)

    def cb(self, msg):
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = PoseRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
