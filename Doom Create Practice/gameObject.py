import numpy as np

import geometry


class game_Object:
    def __init__(self, x=0, y=0, width=0, height=0):
        # GameObject 계층은 pygame을 모르는 순수 게임 상태만 가진다.
        # 이미지를 어떻게 그리고 어떤 키로 움직이는지는 바깥 객체가 담당한다.
        self.x = x
        self.y = y
        self.x_before = x
        self.y_before = y
        self.width = width
        self.height = height
        self.radius = min(width, height) / 2 if width and height else 0
        self.is_alive = True
        self.life_point = 100

    def set_size(self, width, height):
        self.width = width
        self.height = height
        self.radius = min(width, height) / 2
        return self

    def get_pos(self):
        return (self.x, self.y)

    def get_center(self):
        return (self.x + self.width / 2, self.y + self.height / 2)


class Hero(game_Object):
    def __init__(self, screen_size, image_size):
        # Hero는 이미지 자체가 아니라 이미지 크기만 받아서 충돌 반경과 중심점을 계산한다.
        super().__init__(width=image_size[0], height=image_size[1])
        screen_width, screen_height = screen_size
        self.x = screen_width / 2
        self.y = screen_height
        self.x_before = self.x
        self.y_before = self.y

        self.rotate = 0 % 360
        self.vision = 60
        self.v_distance = 1200
        self.attack_range = 300
        self.attack_rad = 30
        self.move_speed = 400
        self.turn_speed = 80

        self.render_x = screen_width / 2
        self.render_y = screen_height - self.radius

    def update(self, input_state, dt, collision_resolver=None):
        # 회전은 이동 벡터를 만들기 전에 먼저 반영한다.
        # 이렇게 해야 같은 프레임의 전진 입력이 새 시선 방향을 따라간다.
        if input_state.is_pressed("turn_left"):
            self.rotate = (self.rotate - self.turn_speed * dt) % 360
        if input_state.is_pressed("turn_right"):
            self.rotate = (self.rotate + self.turn_speed * dt) % 360

        # 입력 상태를 Hero 기준 방향 벡터로 바꾼다.
        # 여기서 Hero는 pygame 키가 아니라 forward/backward 같은 액션만 읽는다.
        forward, right = geometry.movement_vectors(self.rotate)
        movement = np.array([0.0, 0.0], dtype=float)

        if input_state.is_pressed("forward"):
            movement += forward
        if input_state.is_pressed("backward"):
            movement -= forward
        if input_state.is_pressed("strafe_right"):
            movement += right
        if input_state.is_pressed("strafe_left"):
            movement -= right

        # 대각선 이동이 더 빨라지지 않도록 최종 이동 벡터를 정규화한다.
        movement = geometry.normalize(movement)
        if np.linalg.norm(movement) == 0:
            return

        self._move_with_collision(movement * self.move_speed * dt, collision_resolver)

    def _move_with_collision(self, movement, collision_resolver=None):
        # x축과 y축을 나눠 움직이면 벽에 부딪힐 때 한 축만 되돌릴 수 있다.
        # 그래서 벽을 비비며 움직이는 느낌을 만들기 쉽다.
        self.x_before = self.x
        self.x += movement[0]
        if collision_resolver is not None:
            collision_resolver(self, "x")

        self.y_before = self.y
        self.y += movement[1]
        if collision_resolver is not None:
            collision_resolver(self, "y")


class Enemy(game_Object):
    def __init__(self, x=0, y=0, image_size=(30, 30)):
        # Enemy도 이미지 객체는 들고 있지 않고, 충돌에 필요한 크기만 저장한다.
        super().__init__(x=x, y=y, width=image_size[0], height=image_size[1])
        self.move_speed = 60

    def chase(self, target, dt, collision_resolver=None):
        # 적에서 Hero로 향하는 상대 벡터를 만들고, 길이 1의 방향 벡터로 바꾼다.
        target_pos = geometry.as_point(target.get_center())
        enemy_pos = geometry.as_point(self.get_center())
        direction = target_pos - enemy_pos
        dist = np.linalg.norm(direction)

        if dist >= target.v_distance or dist == 0:
            return None

        # 방향은 유지하고, 실제 이동량은 speed * dt로 결정한다.
        direction = direction / dist
        movement = direction * self.move_speed * dt
        self._move_with_collision(movement, collision_resolver)
        return direction

    def _move_with_collision(self, movement, collision_resolver=None):
        # Hero 이동과 같은 방식으로 축별 충돌 처리를 한다.
        self.x_before = self.x
        self.x += movement[0]
        if collision_resolver is not None:
            collision_resolver(self, "x")

        self.y_before = self.y
        self.y += movement[1]
        if collision_resolver is not None:
            collision_resolver(self, "y")


class Wall:
    def __init__(self, x, y, w, h):
        # 벽은 월드 좌표의 직사각형 정보만 가진다.
        # 실제 화면에 어떻게 보일지는 Renderer가 Hero 시점으로 변환해서 그린다.
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def get_pos(self):
        return (self.x, self.y)

    def get_posx(self):
        return (self.x + self.w, self.y)

    def get_posy(self):
        return (self.x, self.y + self.h)

    def get_posxy(self):
        return (self.x + self.w, self.y + self.h)

    def get_center(self):
        return (self.x + self.w / 2, self.y + self.h / 2)

    def get_point_list(self):
        return [tuple(point) for point in self.get_points_array()]

    def get_points_array(self):
        # 큰 벽은 꼭짓점만 보면 시야 판정이 빗나갈 수 있어서 일정 간격으로 샘플 점을 만든다.
        # numpy meshgrid로 벽 내부의 검사 좌표들을 한 번에 생성한다.
        step = 100
        xs = np.arange(self.x, self.x + self.w, step)
        ys = np.arange(self.y, self.y + self.h, step)
        grid_x, grid_y = np.meshgrid(xs, ys)
        return np.column_stack((grid_x.ravel(), grid_y.ravel()))

    def render_points(self):
        # 화면에 벽을 그릴 때 필요한 네 꼭짓점.
        # numpy 배열로 넘기면 Renderer에서 한 번에 좌표 변환하기 좋다.
        return np.array(
            [
                self.get_pos(),
                self.get_posx(),
                self.get_posxy(),
                self.get_posy(),
            ],
            dtype=float,
        )

    def rect_min(self):
        return (min(self.x, self.x + self.w), min(self.y, self.y + self.h))

    def rect_max(self):
        return (max(self.x, self.x + self.w), max(self.y, self.y + self.h))

    def get_mini_walls(self):
        # 긴 벽을 작은 벽 단위로 쪼개고 싶을 때 쓰는 보조 함수.
        # 현재 렌더링에서는 직접 사용하지 않지만, 시야/충돌 최적화 후보로 남겨둔다.
        list_mini_walls = []
        mini_size = 100

        if self.w >= self.h:
            for i in range(self.x, self.x + self.w, mini_size):
                mini_w = min(mini_size, self.x + self.w - i)
                list_mini_walls.append(Wall(i, self.y, mini_w, self.h))
        else:
            for j in range(self.y, self.y + self.h, mini_size):
                mini_h = min(mini_size, self.y + self.h - j)
                list_mini_walls.append(Wall(self.x, j, self.w, mini_h))

        return list_mini_walls


GameObject = game_Object
