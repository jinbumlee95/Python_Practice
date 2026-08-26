import pygame
import random
import math

class game_Object : 
    def __init__(self,main_screen) : 
        self.x = 0
        self.y = 0 
        self.is_alive = True
        self.screen = main_screen
        self.life_point = 100
        
    def set_img(self,addr) :
        self.image = pygame.image.load(addr)
        return self

    def change_size(self,w,h) :
        self.image = pygame.transform.scale(self.image, (w, h))
        return self

    
    def show(self) :
        self.screen.blit(self.image, (self.x,self.y))

    def get_pos(self) :
        return (self.x,self.y)
        
    def get_center(self) :
        return (self.x + self.image.get_size()[0] / 2  ,self.y + self.image.get_size()[1] / 2 )



class Hero(game_Object) : 
    def __init__(self,main_screen) : 
        super().__init__(main_screen)
        self.set_img('images/guy.png')
        self.x = self.screen.get_width() / 2 - self.image.get_size()[0]
        self.y = self.screen.get_height() - self.image.get_size()[1] # 초기 세팅
        self.rotate = 0 % 360  # 각도 처리(360도 기준)
        self.vision = 60 # 정면 120도를 본다 (절반씩 더하고 뺀다?)
        self.v_distance = 1200 # 최대 인식 거리
        self.radius = self.image.get_size()[0]/2 # 반경

        self.render_x = self.screen.get_width() / 2 - self.image.get_size()[0]
        self.render_y = self.screen.get_height() - self.image.get_size()[1]
        
        # 이미지를 계속 회전 시키면 깨지니까, 저장해두고 회전후 세팅할 이미지 하나
        self.orig_image = self.image.copy()

    def rotate_head(self):
        old_center = self.get_center()

        # 3. 원본(orig_image)을 기준으로 회전하여 새로운 image 생성
        self.image = pygame.transform.rotate(self.orig_image, -self.rotate) 
        # pygame ratate 가 반시계 방햐잉 기본이라서

        # 4. 회전 후 바뀐 크기에 맞춰 x, y 좌표를 재조정하여 중심점 유지
        new_w, new_h = self.image.get_size()
        self.x = old_center[0] - new_w / 2
        self.y = old_center[1] - new_h / 2

        return self

    def show(self) :
        #self.screen.blit(self.image, (self.render_x,self.render_y))
        pygame.draw.circle(self.screen, 'red', (self.render_x,self.render_y), self.radius)

class Enemy(game_Object) : 
    def __init__(self,main_screen,x = 0 ,y = 0) : 
        super().__init__(main_screen)
        self.set_img('images/enemy.png').change_size(30,30)
        self.x = x
        self.y = y


    def show(self,hero) :
        # hero의 월드 중심점: 벽을 hero 기준 상대좌표로 바꿀 때 기준점으로 쓴다.
        hero_center_x, hero_center_y = hero.get_center()

        # hero의 화면 렌더 중심점: 상대좌표 계산이 끝난 벽을 화면에 다시 얹는 기준점이다.
        hero_render_center_x = hero.render_x
        hero_render_center_y = hero.render_y

        # 삼각함수는 degree가 아니라 radian을 받기 때문에 rotate 값을 변환한다.
        rad = math.radians(hero.rotate)

        # hero기준의 회전 방향 (x axis)
        right_x = math.cos(rad)
        right_y = math.sin(rad)

        # hero의 논리적 y축 ( hero.rotate == 0  일때 y-axis 인 계산)
        forward_x = math.cos(rad - math.pi / 2)
        forward_y = math.sin(rad - math.pi / 2)

        def to_screen(point) :
            rel_x = point[0] - hero_center_x
            rel_y = point[1] - hero_center_y

            # 상대 위치가 hero의 오른쪽 방향으로 얼마나 떨어져 있는지 계산한다.
            view_x = rel_x * right_x + rel_y * right_y

            # 상대 위치가 hero의 앞쪽 방향으로 얼마나 떨어져 있는지 계산한다.
            view_y = rel_x * forward_x + rel_y * forward_y

            # view_x는 화면 오른쪽이 +라서 더하고, view_y는 앞쪽을 화면 위로 보이게 하려고 뺀다.
            return (int(hero_render_center_x + view_x),
                    int(hero_render_center_y - view_y))
        
        self.screen.blit( self.image, to_screen(self.get_pos()) )
        
        
class Wall():
    def __init__(self,x,y,w,h,main_screen) :
        self.x = x 
        self.y = y
        self.w = w
        self.h = h
        self.screen = main_screen
        
    def get_pos(self) :
        return (self.x,self.y)

    def get_posx(self) :
        return (self.x+self.w,self.y)

    def get_posy(self) :
        return (self.x,self.y+self.h)

    def get_posxy(self) :
        return (self.x+self.w,self.y+self.h)
        
    def get_center(self) :
        return (self.x + self.w/2  ,self.y + self.h/2 )

    def get_point_list(self) :
        point_list = []
        for i in range(self.x, self.x + self.w , 100) :
            for j in range(self.y , self.y + self.h,100) :
                point_list.append( (i,j) ) 
        return point_list

    def get_mini_walls(self) :
        list_mini_walls = []
        mini_size = 100

        if self.w >= self.h:
            for i in range(self.x, self.x + self.w, mini_size) :
                mini_w = min(mini_size, self.x + self.w - i)
                list_mini_walls.append(Wall(i, self.y, mini_w, self.h, self.screen))
        else:
            for j in range(self.y, self.y + self.h, mini_size) :
                mini_h = min(mini_size, self.y + self.h - j)
                list_mini_walls.append(Wall(self.x, j, self.w, mini_h, self.screen))

        return list_mini_walls

    # 벽그리기.. .. 회전이 필요하다.
    def show(self,hero) :
        # 일단 사각형으로 그리는건 성공
        
        # hero의 월드 중심점: 벽을 hero 기준 상대좌표로 바꿀 때 기준점으로 쓴다.
        hero_center_x, hero_center_y = hero.get_center()

        # hero의 화면 렌더 중심점: 상대좌표 계산이 끝난 벽을 화면에 다시 얹는 기준점이다.
        hero_render_center_x = hero.render_x
        hero_render_center_y = hero.render_y

        # 삼각함수는 degree가 아니라 radian을 받기 때문에 rotate 값을 변환한다.
        rad = math.radians(hero.rotate)

        # hero기준의 회전 방향 (x axis)
        right_x = math.cos(rad)
        right_y = math.sin(rad)

        # hero의 논리적 y축 ( hero.rotate == 0  일때 y-axis 인 계산)
        forward_x = math.cos(rad - math.pi / 2)
        forward_y = math.sin(rad - math.pi / 2)

        def to_screen(point) :
            # 벽 꼭짓점의 월드 좌표에서 hero 월드 중심을 빼서 hero 기준 상대 위치로 만든다.
            rel_x = point[0] - hero_center_x
            rel_y = point[1] - hero_center_y

            # 상대 위치가 hero의 오른쪽 방향으로 얼마나 떨어져 있는지 계산한다.
            view_x = rel_x * right_x + rel_y * right_y

            # 상대 위치가 hero의 앞쪽 방향으로 얼마나 떨어져 있는지 계산한다.
            view_y = rel_x * forward_x + rel_y * forward_y

            # view_x는 화면 오른쪽이 +라서 더하고, view_y는 앞쪽을 화면 위로 보이게 하려고 뺀다.
            return (int(hero_render_center_x + view_x),
                    int(hero_render_center_y - view_y))

        # 벽의 네 꼭짓점을 각각 hero 기준 화면 좌표로 변환한다.
        p1 = to_screen(self.get_pos())
        p2 = to_screen(self.get_posx())
        p3 = to_screen(self.get_posy())
        p4 = to_screen(self.get_posxy())

        # 잘 그려지면 좋겠다.
        pygame.draw.polygon(self.screen,(255,255,255), (p1,p2,p4,p3) )
        
