# PR03 - demo.md

## Архитектура ноды patrol

Нода patrol на rclpy:

- подписка на /turtle1/pose - callback только сохраняет последнее сообщение в self._last_pose;
- таймер 0.1 с - публикует geometry_msgs/msg/Twist в относительный топик cmd_vel;
- выбор команды в чистой функции choose_command(pose):
  - pose=None -> нулевая команда;
  - иначе -> linear.x=0.5, angular.z=0.3.

Подписка сохранена полем self._pose_sub, иначе объект может быть удалён сборщиком мусора и callback перестанет вызываться.

## Роли init, spin, callback, Ctrl+C

### rclpy.init(args=args)

Инициализирует контекст rclpy. Вызывается до создания Node. Без него не работают create_subscription, create_publisher, create_timer.

### rclpy.spin(node)

Цикл обработки событий. Без него подписки не получают сообщения, таймеры не срабатывают. Блокирует главный поток до Ctrl+C.

### callback

Функция, вызываемая при событии:
- _pose_callback(msg) - при поступлении сообщения из /turtle1/pose;
- _timer_callback() - при срабатывании таймера каждые 0.1 с.

Callback короткие: подписка сохраняет позу, таймер публикует команду. Логика вынесена в чистую функцию - её можно тестировать без запуска ноды.

### Ctrl+C

SIGINT. rclpy.spin перехватывает его и вызывает context.shutdown(). После выхода из spin:

    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

rclpy.ok() защищает от повторного shutdown - в Jazzy повторный вызов даёт RCLError: rcl_shutdown already called.

После остановки ноды turtlesim не получает новых Twist. Отсутствие процесса patrol - не мгновенная команда торможения; черепаха завершает текущий шаг симуляции и останавливается.

## Сбой: относительное имя cmd_vel

Публикуем в относительный топик cmd_vel. В namespace / он превращается в /cmd_vel. Turtlesim подписан на /turtle1/cmd_vel — это другой топик.

    $ ros2 topic info /cmd_vel --verbose
    Publisher count: 1 (patrol)
    Subscription count: 0

    $ ros2 topic info /turtle1/cmd_vel --verbose
    Publisher count: 0
    Subscription count: 1 (turtlesim)

Черепаха не двигается: у издателя нет подписчиков, у подписчика нет издателей.

## Исправление через remap

    ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel

--ros-args отделяет аргументы ROS от аргументов программы. -r from:=to переименовывает топик внутри ноды: публикации в cmd_vel уходят в /turtle1/cmd_vel.

    $ ros2 topic info /turtle1/cmd_vel --verbose
    Publisher count: 1 (patrol)
    Subscription count: 1 (turtlesim)

Черепаха движется. Поза в /turtle1/pose: linear_velocity=0.5, angular_velocity=0.3 - совпадает с командой.

## Частота команды

    timeout --signal=INT 10s ros2 topic hz /turtle1/cmd_vel

average rate ~ 10.000 Гц, std dev ~ 0.00045 с. Совпадает с таймером 0.1 с. Полный вывод - в evidence/pr03/hz.txt.
