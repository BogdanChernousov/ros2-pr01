from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from patrol.patrol import choose_command, validate_parameters

# Тесты choose_command
def test_choose_command_no_pose():
    cmd = choose_command(None, 0.5, 0.3)
    assert isinstance(cmd, Twist)
    assert cmd.linear.x == 0.0
    assert cmd.angular.z == 0.0

def test_choose_command_with_pose():
    pose = Pose()
    cmd = choose_command(pose, 0.5, 0.3)
    assert cmd.linear.x == 0.5
    assert cmd.angular.z == 0.3

# Тесты валидации параметров
def test_validate_ok():
    assert validate_parameters(0.5, 0.3, 10.0) is True
    assert validate_parameters(0.0, -1.0, 1.0) is True
    assert validate_parameters(1.0, 1.0, 30.0) is True

def test_validate_zero_hz():
    assert validate_parameters(0.5, 0.3, 0.0) is False

def test_validate_negative_hz():
    assert validate_parameters(0.5, 0.3, -5.0) is False

def test_validate_nan_hz():
    assert validate_parameters(0.5, 0.3, float('nan')) is False
