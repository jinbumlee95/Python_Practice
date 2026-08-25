import pygame
import math
import gameObject


raser_list = []
enemy_list = []
screen = None
hero = None
dt = 0.01
color2 = (5, 0, 16)

def init(main_screen) :
    global screen
    global hero
    global enemy_list
    screen = main_screen
    screen.fill(color2)
    hero = gameObject.Hero(screen)

    enemy1 = gameObject.Enemy(screen)
    enemy_list.append(enemy1)



def spwan_enenmy() :
    new_enemy = gameObject.Enemy(screen)
    enemy_list.append(new_enemy)

def move_enemy():
    global enemy_list
    global raser_list
    
    for enemy in enemy_list : 
        enemy.y += 400 * dt
        for raser in raser_list :
            if raser.is_alive and enemy.is_alive: 
                enemy.is_alive = find_col(enemy,raser)# 충돌시 레이저와 적을 둘다 지워야함
                raser.is_alive = find_col(enemy,raser)# 충돌시 레이저와 적을 둘다 지워야함
                if not enemy.is_alive :
                    break
            
    

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
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        hero.x += 400 * dt * math.sin(math.radians(hero.rotate))  
        hero.y -= 400 * dt * math.cos(math.radians(hero.rotate)) # y 방향이 아래가 + 라서 -sin 
    if keys[pygame.K_DOWN]:
        hero.x -= 400 * dt * math.sin(math.radians(hero.rotate))
        hero.y += 400 * dt * math.cos(math.radians(hero.rotate))
    if keys[pygame.K_LEFT]:
        hero.rotate -= 400 * dt
        if hero.rotate <= 0 :
           hero.rotate = 360 + hero.rotate
    if keys[pygame.K_RIGHT]:
        hero.rotate += 400 * dt
        hero.rotate = hero.rotate % 360
        
    hero.rotate_head()
    # for enemy in enemy_list : 
    #     if hero.is_alive:
    #         hero.is_alive = find_col(enemy,hero)
        
    
def render_objects() :
    global raser_list
    global enemy_list
    global hero

    screen.fill(color2)
    
    

    ## 거리 계산
    
    enemy_list = [enemy for enemy in enemy_list if  enemy.is_alive]
    render_enemy_list = [ enemy for enemy in enemy_list if check_render_distance(hero,enemy)]
    
    for enemy in render_enemy_list :
        enemy.show()
    for raser in raser_list :
        raser.show()

    hero.show()
    
    pygame.display.flip()

def game_end() : 
    global hero
    return not hero.is_alive

def check_render_distance(hero,enemy) :
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

    # 그 값이 내 vision cos 값 보다 작으면 시야 안에 있는거임
    min_cos_val = math.cos(math.radians(hero.vision)) # cos(radians(60)) -> 0.5

    return dot >= min_cos_val



    