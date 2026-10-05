import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


def choose_command(pose):
    """Чистая функция: по последней позе вернуть Twist.

    pose=None - поза ещё не получена, выдаём нулевую команду.
    pose=Pose - выдаём движение вперёд с поворотом.
    """
    cmd = Twist()
    if pose is None:
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
    else:
        cmd.linear.x = 0.5
        cmd.angular.z = 0.3
    return cmd


class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol')

        # Последняя полученная поза. Callback только сохраняет сообщение.
        self._last_pose = None

        # Подписка на позу. Сохраняем как поле объекта,
        self._pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self._pose_callback,
            10,
        )

        # Издатель в ОТНОСИТЕЛЬНЫЙ топик cmd_vel.
        # с /turtle1/cmd_vel, куда подписан turtlesim.
        self._cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        # Таймер 0.1 с -> ~10 Гц публикации команды.
        self._timer = self.create_timer(0.1, self._timer_callback)

    def _pose_callback(self, msg):
        self._last_pose = msg

    def _timer_callback(self):
        cmd = choose_command(self._last_pose)
        self._cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
