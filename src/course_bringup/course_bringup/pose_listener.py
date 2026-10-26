import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class PoseListener(Node):
    def __init__(self):
        super().__init__('pose_listener')
        self.declare_parameter('reliability', 'best_effort')
        rel = self.get_parameter('reliability').value

        rel_policy = ReliabilityPolicy.RELIABLE if rel == 'reliable' else ReliabilityPolicy.BEST_EFFORT
        qos = QoSProfile(reliability=rel_policy, history=HistoryPolicy.KEEP_LAST, depth=10)

        self.sub = self.create_subscription(Pose, 'sensor_pose', self.cb, qos)
        self.get_logger().info(f'Listening with reliability: {rel}')

    def cb(self, msg):
        self.get_logger().info(f'Received: x={msg.x:.2f}, y={msg.y:.2f}')

def main(args=None):
    rclpy.init(args=args)
    node = PoseListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
