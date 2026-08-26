import pygame
import math
import gameObject
import Maps

dt = 0.05
color2 = (5, 0, 16)

def init(main_screen) :
    global screen
    global hero
    global enemy_list
    global render_wall_list
    global wall_list
    global hud_font
    
    render_wall_list = []
    enemy_list = []
    screen = main_screen
    screen.fill(color2)
    hero = gameObject.Hero(screen)
    hud_font = pygame.font.SysFont(None, 22)

    wall_list = []
    for wall in Maps.walls :
        new_wall = gameObject.Wall(*wall,screen)
        wall_list.append(new_wall)

    for e in Maps.enemy_spawns :
        enemy = gameObject.Enemy(screen,e[0] ,e[1])
        print(enemy.x, enemy.y)
        enemy_list.append(enemy)
    

def get_Hero() :
    global hero
    return hero


def spwan_enenmy() :
    # 추후에 맵이랑 충돌하지 않으면서 맵 안이면서 hero 주변에 스폰 되도록 하는 장치가 필요함
    new_enemy = gameObject.Enemy(screen,0,0) 
    enemy_list.append(new_enemy)

def move_enemy():
    global enemy_list
    
    for enemy in enemy_list : 
        enemy.y += 400 * dt
            
    

def find_col(obj1, obj2) : 
    ## 현채 위치 + 사이즈로 범위 구간을 찾을 수 있고, 해당 범위 구간 안에 있다면 처리 가능?
    ## pygame 충돌 감지 함수가 있겠지만 직접 구현 해보기
    x_obj1_end = (obj1.x + obj1.image.get_size()[0])
    x_obj2_end = (obj2.x + obj2.image.get_size()[0])

    y_obj1_end = (obj1.y + obj1.image.get_size()[1])
    y_obj2_end = (obj2.y + obj2.image.get_size()[1])

    ## case x-axis 
    check_x = (obj1.x >= obj2.x and x_obj2_end >= obj1.x ) or (obj2.x >= obj1.x and x_obj1_end >= obj2.x ) ## x 값이 서로의 구간 안에 겹친다면
    check_y = (obj1.y >= obj2.y and y_obj2_end >= obj1.y ) or (obj2.y >= obj1.y and y_obj1_end >= obj2.y ) ## y 값이 서로의 구간 안에 겹친다면
    

    return not (check_x and check_y) # 둘다 해당 해야함 > 사망 처리를 위해 False 리턴



# 화면 전환을 각도로 처리하기 위해서는, 캐릭터가 직선으로 움직이는게 아니라, 보고있는 방향으로 움직여야 한다
# Hero class 에서 저장해둔 현재 바라보는 방향 rotate 를 기준으로 x,y 를 움직이는데,
# 통상적인 좌표 환경에서는 x 축이 좌우, y축이 앞 뒤인데, 이는 0도가 x 축이기 때문.
# 이 상황을 뒤집으려면 > 90도 shift  sin cos 반대로 쓰기 > 인데 cos은 우함수 >> y만 반대로 써야 함  (-sin)
def move_hero() :
    global hero

    hero.x_before = hero.x # 이동 전 기존 위치
    hero.y_before = hero.y # 이동 전 기존 위치

    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        hero.x += 400 * dt * math.sin(math.radians(hero.rotate))  
        check_hero_collect_position(hero,'x') 
        hero.y -= 400 * dt * math.cos(math.radians(hero.rotate)) # y 방향이 아래가 + 라서 -sin 
        check_hero_collect_position(hero,'y') 
    if keys[pygame.K_DOWN]:
        hero.x -= 400 * dt * math.sin(math.radians(hero.rotate))
        check_hero_collect_position(hero,'x') 
        hero.y += 400 * dt * math.cos(math.radians(hero.rotate))
        check_hero_collect_position(hero,'y') 
    if keys[pygame.K_LEFT]:
        hero.rotate -= 400 * dt * 0.2
        if hero.rotate <= 0 :
           hero.rotate = 360 + hero.rotate
    if keys[pygame.K_RIGHT]:
        hero.rotate += 400 * dt * 0.2
        hero.rotate = hero.rotate % 360

    
    
    
    #hero.rotate_head() # 현재 hero 가 보고 있는 방향으로 머리 돌려주는거
    # 지도 같은게 필요하면 이거 쓰면 됨
    # for enemy in enemy_list : 
    #     if hero.is_alive:
    #         hero.is_alive = find_col(enemy,hero)
        
    
def render_objects() :
    global enemy_list
    global hero
    global screen
    global render_wall_list
    global wall_list
    
    screen.fill(color2)
    
    ## 거리 계산
    
    enemy_list = [enemy for enemy in enemy_list if  enemy.is_alive]
    render_enemy_list = [ enemy for enemy in enemy_list if check_render_object(hero,enemy) ]
    
    render_wall_list = []
    # 렌더링 할 벽 선택 후 추가.
    for wall in wall_list :
        if check_render_distance_walls(hero, wall) :
            render_wall_list.append(wall)
        # for mini_wall in new_wall.get_mini_walls() :
        #     if check_render_distance_walls(hero, mini_wall) :
        #         render_wall_list.append(mini_wall) # 작은 벽으로 나눠서 그리기 이것도 쓸곳이 있을지도

    
    
    for wall in render_wall_list :
        wall.show(hero)
        
    for enemy in render_enemy_list :
        enemy.show(hero)
    

    hero.show()
    draw_position_hud()
    
    pygame.display.flip()

def game_end() : 
    global hero
    return not hero.is_alive


def draw_position_hud() :
    hero_x, hero_y = hero.get_center()
    text = f"x: {hero_x:.0f}  y: {hero_y:.0f}"
    text_surface = hud_font.render(text, True, (235, 235, 245))

    padding_x = 10
    padding_y = 6
    box_w = text_surface.get_width() + padding_x * 2
    box_h = text_surface.get_height() + padding_y * 2
    box_x = screen.get_width() - box_w - 12
    box_y = screen.get_height() - box_h - 12
    box = pygame.Rect(box_x, box_y, box_w, box_h)

    pygame.draw.rect(screen, (18, 18, 28), box)
    pygame.draw.rect(screen, (110, 110, 130), box, 1)
    screen.blit(text_surface, (box_x + padding_x, box_y + padding_y))

def check_render_object(hero,enemy) :
    #거리 체크 (이미 시야 거리 바깥이면 빠르게 False 반환)
    enemy_pos = enemy.get_center()
    hero_pos = hero.get_center()
    
    dist = math.dist(enemy_pos, hero_pos)
    if dist > hero.v_distance or dist == 0:
        return False

    #  상대 적인 위치를 계산 한 후 상대 위치 저장
    rel_x = (enemy_pos[0] - hero_pos[0]) / dist
    rel_y = (enemy_pos[1] - hero_pos[1]) / dist

    # 캐릭터가 바라보고 있는 방향에 대해서 단위 벡터 생성( sin^2 + cos^2 = 1 이니까 )
    facing_x = math.cos(math.radians(hero.rotate-90)) # 정면을 0 이라고 해서 90도 보정
    facing_y = math.sin(math.radians(hero.rotate-90))

    # 상대적  위치랑 내 시야 랑 내적함
    dot = rel_x * facing_x + rel_y * facing_y

    # 그 값이 내 vision cos 값 보다 크면 시야 안에 있는거임
    min_cos_val = math.cos(math.radians(hero.vision)) # cos(radians(60)) -> 0.5



    # =======================
    visible = True
    between_vector  = (rel_x, rel_y) # 상대 벡터
    
    for wall in wall_list :
        if check_render_distance_walls(hero, wall) : # 일단 랜더링 대상 여부 확인
            p1 = wall.get_pos()
            p2 = wall.get_posx()
            p3 = wall.get_posy()
            p4 = wall.get_posxy()
            
            if line_cross(hero_pos, enemy_pos, p1, p2):
                visible =  False
            if line_cross(hero_pos, enemy_pos, p2, p4):
                visible =  False                
            if line_cross(hero_pos, enemy_pos, p4, p3):
                visible =  False
            if line_cross(hero_pos, enemy_pos, p3, p1):
                visible =  False
            if not visible :
                break # 연산량 아끼기
                

    return dot >= min_cos_val and visible


# 선분 교차 검사 수식 구글링 해서 찾아옴
def ccw(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) # 이 값이 0 을 기준으로 해당 선분의 좌우를 구분함 ( 외적 )

def line_cross(a, b, c, d):
    return ccw(a, b, c) * ccw(a, b, d) <= 0 and ccw(c, d, a) * ccw(c, d, b) <= 0 # 그리고 각 점에 대해서 연산해서 둘다 음수면 충돌함

def check_render_distance_walls(hero,wall) :
    default = False
    #거리 체크 (이미 시야 거리 바깥이면 빠르게 False 반환    
    hero_pos = hero.get_center()

    rel_list = []
    
    for d in wall.get_point_list() :
        dist = math.dist(d, hero_pos) # 벽의 각 점이랑 hero 의 거리를 계산.
        rel_list.append(  ((d[0] - hero_pos[0]) / dist , (d[1] - hero_pos[1]) / dist ) )  
        # 상대적 위치를 미리 계산해서 처리해
        if dist < hero.v_distance and dist != 0: 
            default = True # 일단 점이 하나라도 있으면 처리되어야 하니까..
        
    if not default :
        return default # 1차 거리 계산후에 해당하지 않는다면, 즉시 반환

    
    #  상대 적인 위치를 계산 한 후 상대 위치 저장
    # rel_x = (d[0] - hero_pos[0]) / dist
    # rel_y = (d[1] - hero_pos[1]) / dist

    # 캐릭터가 바라보고 있는 방향에 대해서 단위 벡터 생성( sin^2 + cos^2 = 1 이니까 )
    facing_x = math.cos(math.radians(hero.rotate-90)) # 정면을 0 이라고 해서 90도 보정
    facing_y = math.sin(math.radians(hero.rotate-90))

    # 상대적  위치랑 내 시야 랑 내적함
    #dot = rel_x * facing_x + rel_y * facing_y
    # dot를 개별 에서 전체 보유 리스트를 전부 체크 하고, 최댓값을 리턴 하도록 수정 한것
    dot = max(list( map( lambda x : get_product(x,(facing_x,facing_y)) ,   rel_list ))) 
    
    # 그 값이 내 vision cos 값 보다 크면 시야 안에 있는거임
    min_cos_val = math.cos(math.radians(hero.vision)) # cos(radians(60)) -> 0.5


    

    return dot >= min_cos_val
    
def get_product(v1, v2) :
    return v1[0]*v2[0] + v1[1]*v2[1]


def check_hero_collect_position(hero,axis) :

    closest_wall_list =[]

    for wall in wall_list :
        if find_col_wall(hero, wall,2) : # hero 반경 두배 범위 안의 벽만 찾고 싶어
            closest_wall_list.append(wall)

    if axis == 'x':
        for wall in closest_wall_list :
            # 일단 둘다 인 상황인데? x 제어
            if find_col_wall(hero,wall): 
                hero.x = hero.x_before
                
    else :
        for wall in closest_wall_list :
            # 일단 둘다 인 상황인데? y 제어
            if find_col_wall(hero,wall): 
                hero.y = hero.y_before
                
        
            
    


def find_col_wall(hero, wall , radius_multiplier = 1) : 
    
    hero_pos = hero.get_center()
    radius = hero.radius
    
    closest_point_x = 0

    if hero_pos[0] <= min(wall.get_pos()[0], wall.get_posxy()[0])  :
        closest_point_x = min(wall.get_pos()[0], wall.get_posxy()[0])
    elif hero_pos[0] >= max(wall.get_pos()[0], wall.get_posxy()[0]) :
        closest_point_x = max(wall.get_pos()[0], wall.get_posxy()[0])
    else :
        closest_point_x = hero_pos[0]

    closest_point_y = 0 
    
    if hero_pos[1] <= min(wall.get_pos()[1], wall.get_posxy()[1])  :
        closest_point_y = min(wall.get_pos()[1], wall.get_posxy()[1])
    elif hero_pos[1] >= max(wall.get_pos()[1], wall.get_posxy()[1]) :
        closest_point_y = max(wall.get_pos()[1], wall.get_posxy()[1])
    else :
        closest_point_y = hero_pos[1]

    
    # 제일 가까운 점 을 구했음

    # 이제 이 점과 hero 의 중심사이의 거리가 math.dist(d, hero_pos) , radius 보다 작은지 보면됨


    # 되긴 되는데, 특정 벽은 의도 한 대로 막히는데
    # 또 어떤 벽은 의도대로 안막히는 사항이 있음. 이유가 뭘까? > 집에가서 추가 적인 고민을 해보자.
    return math.dist((closest_point_x,closest_point_y), hero_pos) <= radius * radius_multiplier

