import random

import gameObject
import geometry
import Maps
from asset_manager import AssetManager
from input_handler import InputHandler
from renderer import Renderer


DEFAULT_DT = 1 / 60
SPAWN_TRY_LIMIT = 300
dt = DEFAULT_DT
color2 = (5, 0, 16)

screen = None
hero = None
enemy_list = []
render_wall_list = []
wall_list = []
assets = None
renderer = None
input_handler = None


def init(main_screen):
    # 기존 노트북 호출 흐름을 유지하기 위해 init에서 전체 게임 상태를 한 번에 준비한다.
    # 나중에 Game 클래스로 옮기기 전까지는 doomFunctions가 연결자 역할을 맡는다.
    global screen
    global hero
    global enemy_list
    global render_wall_list
    global wall_list
    global assets
    global renderer
    global input_handler

    screen = main_screen

    # pygame 이미지 처리는 AssetManager에 모아둔다.
    # Hero/Enemy는 Surface를 직접 들고 있지 않고, 필요한 크기만 받아간다.
    assets = AssetManager()
    assets.load_image("hero", "images/guy.png")
    assets.load_image("enemy", "images/enemy.png", size=(30, 30))

    # Renderer와 InputHandler만 pygame의 화면/이벤트 세부사항을 직접 안다.
    renderer = Renderer(screen, assets, color2)
    input_handler = InputHandler()
    hero = gameObject.Hero(screen.get_size(), assets.get_size("hero"))

    # Maps.py의 튜플 데이터를 실제 게임 객체로 바꿔둔다.
    wall_list = [gameObject.Wall(*wall) for wall in Maps.walls]
    enemy_size = assets.get_size("enemy")
    enemy_list = [
        gameObject.Enemy(spawn_x, spawn_y, enemy_size)
        for spawn_x, spawn_y in Maps.enemy_spawns
    ]
    render_wall_list = []


def get_Hero():
    return hero


def get_input_handler():
    return input_handler


def handle_event(event):
    # 메인 루프에서 받은 pygame 이벤트를 입력 상태 객체로 넘긴다.
    # 여기서부터는 pygame 키 코드가 게임 액션 이름으로 바뀐다.
    input_handler.handle_event(event)


def quit_requested():
    return input_handler.quit_requested


def update(frame_dt=None):
    # 한 프레임의 게임 상태 갱신 순서.
    # 입력 처리 결과를 보고 Hero, Enemy 같은 객체들이 자기 상태를 업데이트한다.
    frame_dt = _resolve_dt(frame_dt)

    # 공격은 누르고 있는 동안 매 프레임 나가지 않도록 consume으로 한 번만 처리한다.
    if input_handler.consume("attack"):
        hero_attack()

    move_hero(frame_dt)
    move_enemy(frame_dt)
    input_handler.reset_frame()

def spawn_enemy(max_attempts=SPAWN_TRY_LIMIT):
    # 랜덤 좌표를 여러 번 뽑아보면서 스폰 가능한 위치를 찾는다.
    # 조건을 끝까지 만족하는 후보만 실제 enemy_list에 추가한다.
    enemy = make_random_enemy(max_attempts)
    if enemy is None:
        return None

    enemy_list.append(enemy)
    return enemy


def make_random_enemy(max_attempts=SPAWN_TRY_LIMIT):
    # 스폰 후보를 만들고, Hero 주변 안전거리 밖/벽 미충돌 조건을 검사한다.
    # 실패할 수 있으므로 무한 반복 대신 최대 시도 횟수를 둔다.
    enemy_size = assets.get_size("enemy")

    for _ in range(max_attempts):
        enemy = make_random_enemy_candidate(enemy_size)
        if can_spawn_enemy(enemy):
            return enemy

    return None


def make_random_enemy_candidate(enemy_size):
    # 맵 전체 경계 안에서 적의 좌상단 좌표를 랜덤으로 고른다.
    # 벽과 겹치는지 여부는 can_spawn_enemy에서 따로 검사한다.
    min_x, min_y, max_x, max_y = get_map_bounds()
    enemy_w, enemy_h = enemy_size

    x = random.uniform(min_x, max_x - enemy_w)
    y = random.uniform(min_y, max_y - enemy_h)
    return gameObject.Enemy(x, y, enemy_size)


def get_map_bounds():
    # 현재 맵은 외곽 벽이 전체 영역을 감싸는 구조다.
    # 그래서 모든 벽의 최소/최대 좌표를 이용해 랜덤 스폰 범위를 만든다.
    min_x = min(wall.rect_min()[0] for wall in wall_list)
    min_y = min(wall.rect_min()[1] for wall in wall_list)
    max_x = max(wall.rect_max()[0] for wall in wall_list)
    max_y = max(wall.rect_max()[1] for wall in wall_list)
    return min_x, min_y, max_x, max_y


def can_spawn_enemy(enemy):
    # 벽과 겹치는 위치면 생성하지 않는다.
    if any(find_col_wall(enemy, wall) for wall in wall_list):
        return False

    # 시야 바깥에서 생성 되도록 처리
    if geometry.distance(hero.get_center(), enemy.get_center()) < hero.v_distance:
        return False

    return True


def move_hero(frame_dt=None):
    # 실제 이동 계산은 Hero 내부 메소드가 담당한다.
    # doomFunctions는 충돌 검사 함수를 같이 넘겨주는 연결만 한다.
    hero.update(input_handler, _resolve_dt(frame_dt), check_hero_collect_position)


def move_enemy(frame_dt=None):
    # 적은 Hero 방향으로 이동하되, Hero 시야 거리 안에 있을 때만 추적한다.
    frame_dt = _resolve_dt(frame_dt)

    for enemy in enemy_list:
        direction = enemy.chase(hero, frame_dt, check_hero_collect_position)
        if direction is None:
            continue

        # Hero와 부딪히면 적을 진행 반대 방향으로 밀어내고 HP를 깎는다.
        if check_circle_to_circle_coll(hero, enemy):
            enemy.x = enemy.x_before - direction[0] * 60
            enemy.y = enemy.y_before - direction[1] * 60
            hero.life_point -= 1
            if hero.life_point <= 0:
                hero.is_alive = False


def render_objects():
    # 렌더링 전에 살아있는 적만 남기고, 현재 시야에 들어오는 대상만 골라낸다.
    global enemy_list
    global render_wall_list

    enemy_list = [enemy for enemy in enemy_list if enemy.is_alive]
    render_enemy_list = [
        enemy for enemy in enemy_list if check_render_object(hero, enemy)
    ]
    render_wall_list = [
        wall for wall in wall_list if check_render_distance_walls(hero, wall)
    ]

    # 실제 pygame draw/blit은 Renderer에게 맡긴다.
    renderer.render(hero, render_wall_list, render_enemy_list)


def game_end():
    return not hero.is_alive


def draw_position_hud():
    renderer.draw_position_hud(hero)


def check_render_object(hero, enemy):
    # 먼저 거리와 시야각을 검사해서 보이지 않는 적은 빠르게 제외한다.
    hero_pos = hero.get_center()
    enemy_pos = enemy.get_center()
    facing = geometry.facing_vector(hero.rotate)

    if not geometry.target_in_angle(
        hero_pos,
        enemy_pos,
        facing,
        hero.v_distance,
        hero.vision,
    ):
        return False

    # 각 벽의 네 변과 Hero-Enemy 선분이 교차하면 벽 뒤에 있는 것으로 본다.
    for wall in wall_list:
        if not check_render_distance_walls(hero, wall):
            continue

        p1, p2, p4, p3 = wall.render_points()
        if geometry.line_cross(hero_pos, enemy_pos, p1, p2):
            return False
        if geometry.line_cross(hero_pos, enemy_pos, p2, p4):
            return False
        if geometry.line_cross(hero_pos, enemy_pos, p4, p3):
            return False
        if geometry.line_cross(hero_pos, enemy_pos, p3, p1):
            return False

    return True


def ccw(a, b, c):
    return geometry.ccw(a, b, c)


def line_cross(a, b, c, d):
    return geometry.line_cross(a, b, c, d)


def check_render_distance_walls(hero, wall):
    # 벽의 샘플 점 중 하나라도 Hero 시야 안에 있으면 렌더링 대상으로 본다.
    facing = geometry.facing_vector(hero.rotate)
    return geometry.any_point_in_angle(
        wall.get_points_array(),
        hero.get_center(),
        facing,
        hero.v_distance,
        hero.vision,
    )


def get_product(v1, v2):
    return geometry.dot(v1, v2)


def check_hero_collect_position(obj, axis):
    # 모든 벽을 정밀 검사하면 비싸므로, 반경 두 배 안쪽의 가까운 벽만 먼저 추린다.
    closest_wall_list = [
        wall for wall in wall_list if find_col_wall(obj, wall, radius_multiplier=2)
    ]

    for wall in closest_wall_list:
        if not find_col_wall(obj, wall):
            continue

        # 이동한 축만 되돌린다. 이렇게 하면 벽에 닿아도 다른 축 이동은 살아남는다.
        if axis == "x":
            obj.x = obj.x_before
        else:
            obj.y = obj.y_before


def find_col_wall(obj, wall, radius_multiplier=1):
    # 원형 객체와 직사각형 벽의 충돌 판정.
    # 내부 계산은 geometry에서 numpy 기반으로 처리한다.
    return geometry.circle_intersects_rect(
        obj.get_center(),
        obj.radius,
        wall.rect_min(),
        wall.rect_max(),
        radius_multiplier,
    )


def check_circle_to_circle_coll(c1, c2):
    return geometry.circle_intersects_circle(
        c1.get_center(),
        c1.radius,
        c2.get_center(),
        c2.radius,
    )


def hero_attack():
    # 공격 범위와 시야를 동시에 만족하는 적만 제거한다.
    attack_list = [
        enemy
        for enemy in enemy_list
        if check_render_object(hero, enemy) and is_enemey_inrange(hero, enemy)
    ]

    for enemy in attack_list:
        enemy.is_alive = False


def is_enemey_inrange(hero, enemy):
    # 공격 판정은 시야 판정보다 짧은 거리와 좁은 각도를 사용한다.
    return geometry.target_in_angle(
        hero.get_center(),
        enemy.get_center(),
        geometry.facing_vector(hero.rotate),
        hero.attack_range,
        hero.attack_rad,
    )


def find_col(obj1, obj2):
    # 사각형 충돌 함수.
    obj1_x_end = obj1.x + obj1.width
    obj2_x_end = obj2.x + obj2.width
    obj1_y_end = obj1.y + obj1.height
    obj2_y_end = obj2.y + obj2.height

    check_x = (obj1.x <= obj2_x_end) and (obj2.x <= obj1_x_end)
    check_y = (obj1.y <= obj2_y_end) and (obj2.y <= obj1_y_end)
    return not (check_x and check_y)


def _resolve_dt(frame_dt):
    # 새 루프에서는 dt를 넘기지만, 예전처럼 인자 없이 불러도 기본값으로 동작하게 한다.
    return DEFAULT_DT if frame_dt is None else frame_dt
