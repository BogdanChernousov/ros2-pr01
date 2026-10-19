import math
import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


def validate_parameters(linear_speed, turn_rate, publish_hz):
    if math.isnan(linear_speed) or math.isnan(turn_rate) or math.isnan(publish_hz):
        return False
    if not (0.0 <= linear_speed <= 1.0):
        return False
    if not (-1.0 <= turn_rate <= 1.0):
        return False
    if not (1.0 <= publish_hz <= 30.0):
        return False
    return True


def choose_command(pose, linear_speed, turn_rate):
    cmd = Twist()
    if pose is None:
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
    else:
        cmd.linear.x = linear_speed
        cmd.angular.z = turn_rate
    return cmd


class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol')

        # Объявление параметров
        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('turn_rate', 0.3)
        self.declare_parameter('publish_hz', 10.0)

        # Чтение параметров
        self._linear_speed = self.get_parameter('linear_speed').value
        self._turn_rate = self.get_parameter('turn_rate').value
        self._publish_hz = self.get_parameter('publish_hz').value

        # Подписка на позу
        self._last_pose = None
        self._pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self._pose_callback, 10)

        # Издатель в относительный cmd_vel
        self._cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        # Таймер
        self._timer = self.create_timer(1.0 / self._publish_hz, self._timer_callback)

        # Регистрация колбэка для смены параметров
        self.add_on_set_parameters_callback(self._parameter_callback)

    def _pose_callback(self, msg):
        self._last_pose = msg

    def _timer_callback(self):
        cmd = choose_command(self._last_pose, self._linear_speed, self._turn_rate)
        self._cmd_pub.publish(cmd)

    def _parameter_callback(self, params):
        # Собираем новые значения (сохраняя старые, если не пришли)
        new_linear = self._linear_speed
        new_turn = self._turn_rate
        new_hz = self._publish_hz

        for param in params:
            if param.name == 'linear_speed':
                new_linear = param.value
            elif param.name == 'turn_rate':
                new_turn = param.value
            elif param.name == 'publish_hz':
                new_hz = param.value

        if not validate_parameters(new_linear, new_turn, new_hz):
            self.get_logger().warn('Отклонено обновление параметров: некорректные значения')
            return SetParametersResult(successful=False)

        if new_hz != self._publish_hz:
            self.destroy_timer(self._timer)
            self._timer = self.create_timer(1.0 / new_hz, self._timer_callback)

        self._linear_speed = new_linear
        self._turn_rate = new_turn
        self._publish_hz = new_hz

        return SetParametersResult(successful=True)


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
