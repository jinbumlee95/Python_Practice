import pygame
import random

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
        self.v_distance = 700 # 최대 인식 거리

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

class Enemy(game_Object) : 
    def __init__(self,main_screen) : 
        super().__init__(main_screen)
        self.set_img('images/enemy.png').change_size(30,30)
        self.x = random.randint(60,self.screen.get_width() - self.image.get_size()[0])
        self.y = random.randint(20,100)

        
        
    