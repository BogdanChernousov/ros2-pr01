# ПР01 — граф ROS 2 и разрыв связи через ROS_DOMAIN_ID

## Среда

Ubuntu 24.04.4 LTS, ROS 2 Jazzy, native (dual-boot).
RMW: rmw_fastrtps_cpp. Пакет turtlesim.
Домены: 16 (основной), 17 (для разрыва).

## Исправный граф (домен 16)

Ноды:

    $ ros2 node list --no-daemon --spin-time 2
    /teleop_turtle
    /turtlesim

/turtlesim — симулятор, публикует /turtle1/pose и /turtle1/color_sensor,
подписан на /turtle1/cmd_vel.
/teleop_turtle — управление с клавиатуры, публикует /turtle1/cmd_vel.

Топики и типы:

    $ ros2 topic list -t
    /parameter_events [rcl_interfaces/msg/ParameterEvent]
    /rosout [rcl_interfaces/msg/Log]
    /turtle1/cmd_vel [geometry_msgs/msg/Twist]
    /turtle1/color_sensor [turtlesim/msg/Color]
    /turtle1/pose [turtlesim/msg/Pose]

Тип позы в Jazzy — turtlesim/msg/Pose.

Поза (фрагмент):

    $ ros2 topic echo /turtle1/pose --once
    x: 1.49
    y: 7.77
    linear_velocity: 0.0
    angular_velocity: 0.0

Частота:

    $ time timeout --signal=INT 15s ros2 topic hz /turtle1/pose

- elapsed_seconds = 15.154
- exit = 124 (таймаут, для hz это нормально)
- average rate ≈ 62.5 Гц, отклонение небольшое

## Разрыв связи (домен 17)

Симулятор остаётся в 16. Teleop перезапускаю в 17:

    export ROS_DOMAIN_ID=17
    ros2 run turtlesim turtle_teleop_key

Проверка в домене 17:

    $ ros2 node list --no-daemon --spin-time 2
    /teleop_turtle

/turtlesim не виден. Поза не приходит:

    $ timeout 5s ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once
    exit=124

Стрелки в B больше не двигают черепаху.

Дополнительно прочитал позу с префиксом домена 16:

    $ ROS_DOMAIN_ID=16 ros2 topic echo /turtle1/pose --once
    x: 1.49
    y: 7.77

Симулятор жив и публикует, значит проблема именно в домене.

## Восстановление (домен 16)

Teleop перезапущен в 16:

    export ROS_DOMAIN_ID=16
    ros2 run turtlesim turtle_teleop_key

Проверка:

    $ ros2 node list --no-daemon --spin-time 2
    /teleop_turtle
    /turtlesim

    $ timeout 5s ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once
    exit=0

Поза приходит, стрелки снова двигают черепаху.

## Сравнение

| Состояние | Домены (sim/teleop) | nodes | pose | exit |
|---|---|---|---|---|
| До | 16 / 16 | /turtlesim, /teleop_turtle | приходит | — |
| Сбой | 16 / 17 | только /teleop_turtle | не приходит | 124 |
| После | 16 / 16 | /turtlesim, /teleop_turtle | приходит | 0 |

## Почему перезапускал teleop, а симулятор нет

ROS_DOMAIN_ID читается при запуске ноды. Уже запущенная нода
остаётся в своём домене, export её не перенастраивает. Поэтому
teleop нужно остановить и запустить заново. Симулятор всё время
работал в 16 — его трогать не нужно.
