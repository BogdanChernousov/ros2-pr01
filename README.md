# ПР01 — окружение и граф ROS 2

## Среда

Ubuntu 24.04, ROS 2 Jazzy, native Ubuntu (dual-boot).
Пакет turtlesim. Gazebo не устанавливал — для этой работы не нужен.

## Запуск

Три терминала, в каждом:

    source /opt/ros/jazzy/setup.bash
    export ROS_DOMAIN_ID=16

Терминал A — симулятор:

    ros2 run turtlesim turtlesim_node

Терминал B — управление. Стрелки двигают черепаху, когда фокус
в этом терминале:

    ros2 run turtlesim turtle_teleop_key

Терминал C — наблюдение:

    ros2 node list --no-daemon --spin-time 2
    ros2 topic list -t
    ros2 node info /turtlesim
    ros2 topic type /turtle1/pose
    POSE_TYPE=$(ros2 topic type /turtle1/pose)
    ros2 topic echo /turtle1/pose --once
    ros2 topic hz /turtle1/pose

Тип позы в Jazzy — turtlesim/msg/Pose.
Команду hz держу не меньше 10 секунд, потом Ctrl+C.

## Разрыв связи

В B останавливаю teleop (Ctrl+C) и запускаю заново в другом домене:

    export ROS_DOMAIN_ID=17
    ros2 run turtlesim turtle_teleop_key

В C тоже перехожу в 17 и проверяю:

    export ROS_DOMAIN_ID=17
    ros2 node list --no-daemon --spin-time 2
    timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once

Ожидается: в списке нод только teleop, поза не приходит,
команда завершается по таймауту.

## Восстановление

В B возвращаю teleop в домен 16, в C повторяю проверку в 16.
Обе ноды видны, поза приходит, стрелки снова двигают черепаху.

Причина сбоя: ROS_DOMAIN_ID применяется при запуске ноды.
Уже запущенная нода остаётся в своём домене, export её не
перенастраивает. Поэтому teleop перезапускаю, а симулятор
трогать не нужно.

## Evidence

    evidence/pr01/doctor.txt
    evidence/pr01/graph.md
    evidence/pr01/environment.json
    evidence/pr01/report.json

## Проверка

    python3 -m json.tool evidence/pr01/environment.json > /dev/null
    python3 .course-kit/v1/tools/check_practice.py PR01 --submission .
