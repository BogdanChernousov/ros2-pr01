from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from patrol.patrol import choose_command


def test_choose_command_no_pose():
    """Без позы - нулевая команда."""
    cmd = choose_command(None)
    assert isinstance(cmd, Twist)
    assert cmd.linear.x == 0.0
    assert cmd.angular.z == 0.0


def test_choose_command_with_pose():
    """С обычной позой - движение вперёд с поворотом."""
    pose = Pose()
    pose.x = 5.5
    pose.y = 5.5
    pose.theta = 0.0
    cmd = choose_command(pose)
    assert cmd.linear.x == 0.5
    assert cmd.angular.z == 0.3
