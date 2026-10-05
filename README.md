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


---

# ПР02 — терминал, пакет и запуск turtlesim

## Среда

Тот же репозиторий, Ubuntu 24.04, ROS 2 Jazzy, native.
Course kit v1-w04.

## Пакет

src/turtle_bringup/ — ament_python пакет с launch-файлом.
Зависимости: launch, launch_ros, turtlesim.
В setup.py добавлен glob и запись data_files для launch.

## Сборка

Терминал 1 (только базовая ROS):

    source /opt/ros/jazzy/setup.bash
    colcon build --symlink-install --packages-select turtle_bringup \
      2>&1 | tee evidence/pr02/build.txt

## Запуск

Терминал 2 (ROS + overlay):

    source /opt/ros/jazzy/setup.bash
    source install/setup.bash
    export ROS_DOMAIN_ID=16
    ros2 launch turtle_bringup sim.launch.py

В Терминале 1: ros2 node list --no-daemon --spin-time 2 видит /turtlesim.
Ctrl+C в Терминале 2 останавливает turtlesim.

## Связь команды с движением

Терминал 3:

    ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
      '{linear: {x: 1.0}, angular: {z: 0.5}}'

Поза до/после — ros2 topic echo /turtle1/pose --once в Терминале 1.

## Сбой и исправление

Сбой: команда в /cmd_vel — издатель есть, подписчиков нет, черепаха стоит.
Исправление: то же сообщение в /turtle1/cmd_vel.

## Evidence

    evidence/pr02/
    ├── build-empty.txt
    ├── build.txt
    ├── commands.md
    ├── types.md
    └── report.json

## Проверка

    python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
    python3 .course-kit/v1/tools/check_practice.py PR02 --submission .



# ПР03 — первая нода: поза и команда

## Среда

Тот же репозиторий, Ubuntu 24.04, ROS 2 Jazzy, native.
Course kit v1-w05.

## Пакет

src/patrol/ — ament_python пакет с нодой patrol.
Зависимости: rclpy, geometry_msgs, turtlesim (для типа Pose).

Нода patrol:
- подписка на /turtle1/pose, callback сохраняет последнее сообщение;
- таймер 0.1 с, публикует geometry_msgs/msg/Twist в относительный cmd_vel;
- чистая функция choose_command(pose) выбирает команду.

## Сборка и тесты

    source /opt/ros/jazzy/setup.bash
    colcon build --symlink-install --packages-select patrol
    source install/setup.bash
    python3 -m pytest src/patrol/test

## Запуск (с remap)

    ros2 run turtlesim turtlesim_node       # в отдельном терминале
    ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel

Без remap нода публикует в /cmd_vel, где нет подписчиков.
С remap команда приходит в /turtle1/cmd_vel, и черепаха двигается.

## Частота команды

    timeout --signal=INT 10s ros2 topic hz /turtle1/cmd_vel

Ожидаемо ~10 Гц (таймер 0.1 с).

## Evidence

    evidence/pr03/
    ├── demo.md
    ├── hz.txt
    ├── tests.txt
    └── report.json

## Проверка

    python3 -m pytest src/patrol/test
    python3 .course-kit/v1/tools/check_practice.py PR03 --submission .
