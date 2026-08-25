import pygame
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
    screen = main_screen
    screen.fill(color2)
    hero = gameObject.Hero(screen)

def shoot_raser() : 
    global hero
    new_Raser = gameObject.Raser(hero)
    raser_list.append(new_Raser)

def move_raser():
    global raser_list
    global enemy_list
    
    for raser in raser_list : 
        raser.y -= 400  * dt * 5 # 레이저는 빨리 나가서 맞춰야 하니까 속도 5배
        for enemy in enemy_list :
            if raser.is_alive and enemy.is_alive: 
                enemy.is_alive = find_col(enemy,raser)
                raser.is_alive = find_col(enemy,raser)
                if not enemy.is_alive :
                    break

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


def move_hero() :
    global hero
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        hero.y -= 400 * dt
        hero.y = max(hero.y, hero.image.get_size()[1])
    if keys[pygame.K_DOWN]:
        hero.y += 400 * dt
        hero.y = min(hero.y,screen.get_height() - hero.image.get_size()[1])
    if keys[pygame.K_LEFT]:
        hero.x -= 400 * dt
        hero.x = max(hero.x,0)
    if keys[pygame.K_RIGHT]:
        hero.x += 400 * dt
        hero.x = min(hero.x,screen.get_width() - hero.image.get_size()[0])

    for enemy in enemy_list : 
        if hero.is_alive:
            hero.is_alive = find_col(enemy,hero)# 충돌시 플레이어 사망
        
    
def render_objects() :
    global raser_list
    global enemy_list
    global hero

    screen.fill(color2)
    
    hero.show()
    
    raser_list = [raser for raser in raser_list if raser.y >= 0 and raser.is_alive]
    enemy_list = [enemy for enemy in enemy_list if enemy.y <= screen.get_height() and enemy.is_alive]
    
    for enemy in enemy_list :
        enemy.show()
    for raser in raser_list :
        raser.show()

    pygame.display.flip()

def game_end() : 
    global hero
    return not hero.is_alive