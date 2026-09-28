# PR02 - types.md

## Основные топики

### /turtle1/cmd_vel - geometry_msgs/msg/Twist

Топик команд движения. Издатель - `ros2 topic pub` (или `turtle_teleop_key`), подписчик - `/turtlesim`.

Поля `Twist`:

- `linear` (Vector3) - линейная скорость по осям x, y, z, м/с. В turtlesim используется только `linear.x`  движение вперёд/назад.
- `angular` (Vector3) - угловая скорость вокруг осей x, y, z, рад/с. В turtlesim используется только `angular.z`  поворот в плоскости.

Пример: `{linear: {x: 1.0}, angular: {z: 0.5}}` - вперёд со скоростью 1.0 и поворот против часовой со скоростью 0.5.

### /turtle1/pose - turtlesim/msg/Pose

Топик положения черепахи. Издатель - `/turtlesim`, подписчиков может быть много.

Поля `Pose`:

- `x`, `y` (float64) - координаты черепахи в поле turtlesim.
- `theta` (float64) - угол поворота, радианы.
- `linear_velocity`, `angular_velocity` (float64) - текущие скорости.

## Итог

| Топик | Тип | Роль |
|---|---|---|
| /turtle1/cmd_vel | geometry_msgs/msg/Twist | команды движения |
| /turtle1/pose | turtlesim/msg/Pose | положение и скорости черепахи |
