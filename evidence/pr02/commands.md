# PR02 - commands.md

## Три Linux-команды

### tee (в составе colcon build ... 2>&1 | tee evidence/pr02/build.txt)

Назначение: одновременно вывести поток на экран и записать в файл.
Результат: лог сборки сохранён в `evidence/pr02/build.txt` и показан в терминале.

### source (в составе `source /opt/ros/jazzy/setup.bash`)

Назначение: выполнить скрипт в текущей оболочке, чтобы переменные окружения (PATH, AMENT_PREFIX_PATH и др.) остались в этом терминале.
Результат: `ros2`, `colcon` и другие ROS-команды доступны в текущем терминале; `printenv ROS_DISTRO` возвращает `jazzy`.

### export (в составе `export ROS_DOMAIN_ID=16`)

Назначение: задать переменную окружения текущего терминала, которую увидят все запускаемые в нём процессы.
Результат: `printenv ROS_DOMAIN_ID` возвращает `16`; ноды, запущенные в этом терминале, работают в домене 16.

## Чем `>` отличается от `|`

`>` перенаправляет stdout в файл (перезаписывает). `|` передаёт stdout одной команды на stdin следующей.

Пример: `ros2 doctor --report > doctor.txt` - запись в файл; `ros2 topic list -t | grep cmd` — фильтрация потока.

## Чем `source` отличается от запуска новой программы

`source` выполняет скрипт в текущей оболочке: переменные окружения остаются в текущем терминале.
Запуск новой программы создаёт дочерний процесс: изменения окружения не влияют на родительскую оболочку.

Пример: `source /opt/ros/jazzy/setup.bash` меняет PATH текущего терминала; `bash /opt/ros/jazzy/setup.bash` запустит скрипт в отдельном процессе, PATH родителя не изменится.

## Запуск launch и проверка

    ros2 pkg prefix turtle_bringup
    ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
    ros2 launch turtle_bringup sim.launch.py

`ls` показывает `sim.launch.py` - data_files в setup.py сработал.

В другом терминале: `ros2 node list --no-daemon --spin-time 2` -> `/turtlesim`.

Ctrl+C в терминале launch: turtlesim завершается (`process has finished cleanly`), `node list` пуст.

## Связь команды с движением

Поза ДО:

    $ ros2 topic echo /turtle1/pose --once
    x: 5.544444561004639
    y: 5.544444561004639
    theta: 0.0
    linear_velocity: 0.0
    angular_velocity: 0.0

Команда в B:

    $ ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
      '{linear: {x: 1.0}, angular: {z: 0.5}}'
    publishing #1: geometry_msgs.msg.Twist(linear=...x=1.0..., angular=...z=0.5...)

Поза ПОСЛЕ:

    x: 6.509308815002441
    y: 5.796990871429443
    theta: 0.5040000081062317

Черепаха сдвинулась и повернула. Одна публикация не задаёт бесконечное движение - без новых команд turtlesim останавливается.

## Сбой

    $ ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
      /cmd_vel geometry_msgs/msg/Twist \
      '{linear: {x: 1.0}, angular: {z: 0.5}}'

    $ ros2 topic info /cmd_vel --verbose
    Publisher count: 1
      Node name: _ros2cli_9311
    Subscription count: 0

    $ ros2 topic info /turtle1/cmd_vel --verbose
    Publisher count: 0
    Subscription count: 1
      Node name: turtlesim

Черепаха не движется: у издателя в `/cmd_vel` нет подписчиков.

## Исправление

Изменено только имя топика: `/cmd_vel` -> `/turtle1/cmd_vel`.

    $ ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
      /turtle1/cmd_vel geometry_msgs/msg/Twist \
      '{linear: {x: 1.0}, angular: {z: 0.5}}'

    $ ros2 topic info /turtle1/cmd_vel --verbose
    Publisher count: 1
    Subscription count: 1
      Node name: turtlesim

Поза во время движения:

    x: 7.536332607269287
    y: 7.566099643707275
    theta: 1.5776294469833374
    linear_velocity: 1.0
    angular_velocity: 0.5

После остановки издателя (Ctrl+C):

    linear_velocity: 0.0
    angular_velocity: 0.0

## Сравнение «до / сбой / после»

| Состояние | Топик | Publisher | Subscription | Движение |
|---|---|---|---|---|
| До | /turtle1/cmd_vel | 1 | 1 (turtlesim) | есть |
| Сбой | /cmd_vel | 1 | 0 | нет |
| После | /turtle1/cmd_vel | 1 | 1 | есть |

## Почему правильного типа недостаточно

Тип Twist в обоих топиках совпадает — `geometry_msgs/msg/Twist`. Но издатель и подписчик связываются по **полному имени топика**, а не по типу. Turtlesim подписан именно на `/turtle1/cmd_vel`. Сообщения в `/cmd_vel` уходят в топик без подписчиков. Обнаружение издателя в графе не означает доставку.
