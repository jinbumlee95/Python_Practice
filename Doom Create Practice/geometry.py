import math

import numpy as np


def as_point(value):
    # 좌표 튜플/리스트를 numpy 계산이 가능한 float 벡터로 맞춘다.
    return np.asarray(value, dtype=float)


def distance(a, b):
    # 두 점 사이의 거리 계산. math.dist 대신 numpy 벡터 길이를 사용한다.
    return float(np.linalg.norm(as_point(a) - as_point(b)))


def normalize(vector):
    # 방향 벡터의 길이를 1로 맞춘다.
    # 0 벡터는 나눌 수 없으므로 그대로 반환한다.
    vector = np.asarray(vector, dtype=float)
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def dot(v1, v2):
    # 두 방향이 얼마나 같은 방향을 보는지 확인할 때 쓰는 내적.
    return float(np.dot(as_point(v1), as_point(v2)))


def facing_vector(rotate):
    # 기존 설계에서는 rotate == 0 일 때 화면 위쪽/월드의 -y 방향을 본다.
    # 삼각함수 기준 0도는 +x 방향이라서 90도 보정을 넣는다.
    rad = math.radians(rotate - 90)
    return np.array([math.cos(rad), math.sin(rad)], dtype=float)


def movement_vectors(rotate):
    # Hero 기준 전진 방향과 오른쪽 방향을 한 번에 만든다.
    # 전진은 rotate == 0 일 때 y가 감소해야 하므로 [sin, -cos] 형태를 사용한다.
    rad = math.radians(rotate)
    forward = np.array([math.sin(rad), -math.cos(rad)], dtype=float)
    right = np.array([math.cos(rad), math.sin(rad)], dtype=float)
    return forward, right


def view_axes(rotate):
    # 월드 좌표를 Hero 시점의 화면 좌표로 바꿀 때 사용할 x축/right, y축/forward.
    rad = math.radians(rotate)
    right = np.array([math.cos(rad), math.sin(rad)], dtype=float)
    forward = np.array([math.cos(rad - math.pi / 2), math.sin(rad - math.pi / 2)], dtype=float)
    return right, forward


def world_points_to_screen(points, hero):
    # 여러 월드 좌표를 한 번에 Hero 기준 화면 좌표로 변환한다.
    # 점마다 반복문으로 계산하던 내적을 numpy 배열 연산으로 묶은 부분이다.
    points = np.asarray(points, dtype=float)
    hero_center = as_point(hero.get_center())
    hero_render_center = np.array([hero.render_x, hero.render_y], dtype=float)
    right, forward = view_axes(hero.rotate)

    relative = points - hero_center
    view_x = relative @ right
    view_y = relative @ forward

    screen_points = np.column_stack(
        [
            hero_render_center[0] + view_x,
            hero_render_center[1] - view_y,
        ]
    )
    return [tuple(point.astype(int)) for point in screen_points]


def target_in_angle(origin, target, facing, max_distance, half_angle):
    # 대상이 거리 안에 있고, 바라보는 방향의 시야각 안에 있는지 검사한다.
    # 단위 벡터끼리 내적하면 cos(theta)가 나오므로 각도 비교가 쉬워진다.
    origin = as_point(origin)
    target = as_point(target)
    rel = target - origin
    dist = np.linalg.norm(rel)

    if dist > max_distance or dist == 0:
        return False

    rel_unit = rel / dist
    min_cos_val = math.cos(math.radians(half_angle))
    return dot(rel_unit, facing) >= min_cos_val


def any_point_in_angle(points, origin, facing, max_distance, half_angle):
    # 벽은 면적이 있으므로 여러 샘플 점 중 하나라도 시야에 들어오면 렌더링 대상으로 본다.
    # 거리 필터를 먼저 걸어서 불필요한 내적 계산을 줄인다.
    points = np.asarray(points, dtype=float)
    origin = as_point(origin)
    relative = points - origin
    distances = np.linalg.norm(relative, axis=1)
    in_distance = (distances < max_distance) & (distances != 0)

    if not np.any(in_distance):
        return False

    rel_units = relative[in_distance] / distances[in_distance, None]
    min_cos_val = math.cos(math.radians(half_angle))
    return bool(np.max(rel_units @ as_point(facing)) >= min_cos_val)


def circle_intersects_rect(center, radius, rect_min, rect_max, radius_multiplier=1):
    # 원과 직사각형 충돌 검사.
    center = as_point(center)
    rect_min = as_point(rect_min)
    rect_max = as_point(rect_max)
    closest_point = np.clip(center, rect_min, rect_max)
    return distance(closest_point, center) <= radius * radius_multiplier


def circle_intersects_circle(center1, radius1, center2, radius2):
    # 두 원의 중심 거리가 반지름 합보다 작거나 같으면 충돌이다.
    return distance(center1, center2) <= radius1 + radius2


def ccw(a, b, c):
    # 세 점의 외적 부호로 c가 선분 ab 기준 어느 쪽에 있는지 확인한다.
    a = as_point(a)
    b = as_point(b)
    c = as_point(c)
    ab = b - a
    ac = c - a
    return float(ab[0] * ac[1] - ab[1] * ac[0])


def _ranges_overlap(a1, a2, b1, b2):
    # 두 선분이 같은 직선 위에 있을 때, 각 축의 범위가 겹치는지 확인한다.
    return max(min(a1, a2), min(b1, b2)) <= min(max(a1, a2), max(b1, b2))


def line_cross(a, b, c, d):
    # 선분 ab와 cd가 교차하는지 검사한다.
    # 적과 Hero 사이에 벽 변이 끼어 있는지 판단할 때 사용한다.
    ab_c = ccw(a, b, c)
    ab_d = ccw(a, b, d)
    cd_a = ccw(c, d, a)
    cd_b = ccw(c, d, b)

    if ab_c == ab_d == cd_a == cd_b == 0:
        return (
            _ranges_overlap(a[0], b[0], c[0], d[0])
            and _ranges_overlap(a[1], b[1], c[1], d[1])
        )

    return ab_c * ab_d <= 0 and cd_a * cd_b <= 0
