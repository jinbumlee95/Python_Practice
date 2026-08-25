import pygame
import random

class game_Object : 
    def __init__(self,main_screen) : 
        self.x = 0
        self.y = 0 
        self.is_alive = True
        self.screen = main_screen
        
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
        self.set_img('pyGame/hero2.png').change_size(30,30)   
        self.x = self.screen.get_width() / 2 - self.image.get_size()[0]
        self.y = self.screen.get_height() - 80 # 초기 세팅
        


class Raser(game_Object) : 
    def __init__(self,hero) : 
        self.screen = hero.screen
        self.set_img('pyGame/raser.png')
        self.x , self.y = hero.get_center()
        self.x -= self.image.get_size()[0]/2
        self.is_alive = True
        

class Enemy(game_Object) : 
    def __init__(self,main_screen) : 
        super().__init__(main_screen)
        self.set_img('pyGame/enemy.png').change_size(30,30)
        self.x = random.randint(60,self.screen.get_width() - self.image.get_size()[0])
        self.y = random.randint(20,100)

        
        
    