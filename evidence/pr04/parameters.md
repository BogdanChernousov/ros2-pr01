# PR04 - parameters.md

## 1. Успешная смена частоты (10 -> 5 Гц)

Изначально частота таймера 10 Гц (период 0.1 с).

    $ ros2 param set /patrol publish_hz 5.0
    Set parameter successful

    $ timeout 5s ros2 topic hz /turtle1/cmd_vel
    average rate: 4.997
    average rate: 5.000

Таймер пересоздан, старый уничтожен. Двух одновременных таймеров нет.

## 2. Дефект - отключенная проверка

Временно закомментирована проверка `if not validate_parameters(...)` в `_parameter_callback`.
При попытке установить `publish_hz = 0.0` происходит деление на ноль.

    $ ros2 param set /patrol publish_hz 0.0

Traceback из терминала с нодой:

    File ".../patrol.py", line 88, in _parameter_callback
        self._timer = self.create_timer(1.0 / new_hz, self._timer_callback)
    ZeroDivisionError: float division by zero
    [ros2run]: Process exited with failure 1

Значение 0.0 вызывает отказ (нода падает), потому что период таймера вычисляется как 1.0 / 0.0.

## 3. Исправление

Проверка возвращена. Код валидации:

    if not validate_parameters(new_linear, new_turn, new_hz):
        self.get_logger().warn('Отклонено обновление параметров: некорректные значения')
        return SetParametersResult(successful=False)

    $ ros2 param set /patrol publish_hz 0.0
    Setting parameter failed

В терминале ноды:
    [WARN] [patrol]: Отклонено обновление параметров: некорректные значения

Ноль отклонён, нода не падает. Старая частота (5 Гц) сохранена, поток не прерывается.

## 4. Сервисы и действия

    $ ros2 service list | grep clear
    /clear

    $ ros2 service call /clear std_srvs/srv/Empty
    requester: making request: std_srvs.srv.Empty_Request()
    response:
    std_srvs.srv.Empty_Response()

    $ ros2 action list -t
    /turtle1/rotate_absolute [turtlesim/action/RotateAbsolute]

**Сервис и действие (отличие):**
Сервис `/clear` - синхронный запрос-ответ: очистить экран, получить пустой ответ и ждать его. Действие `/turtle1/rotate_absolute` - долгая операция с обратной связью: клиент отправляет цель, сервер шлёт промежуточные результаты и итог. Действие можно отменить, сервис - нет.
