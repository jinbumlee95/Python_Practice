import pygame

import geometry


class Renderer:
    def __init__(self, screen, assets, background_color=(5, 0, 16)):
        # Renderer는 pygame 화면 객체를 알고 있는 출력 담당자다.
        # 게임 객체의 상태를 읽어서 실제 화면에 그리는 일만 한다.
        self.screen = screen
        self.assets = assets
        self.background_color = background_color
        self.hud_font = pygame.font.SysFont(None, 22)

    def clear(self):
        self.screen.fill(self.background_color)

    def draw_wall(self, hero, wall):
        # 월드 좌표의 벽 꼭짓점을 Hero 시점의 화면 좌표로 변환한 뒤 다각형으로 그린다.
        p1, p2, p4, p3 = geometry.world_points_to_screen(wall.render_points(), hero)
        pygame.draw.polygon(self.screen, (255, 255, 255), (p1, p2, p4, p3))

    def draw_enemy(self, hero, enemy):
        # Enemy는 자신의 위치만 알고, 이미지는 AssetManager에서 가져와 Renderer가 blit한다.
        image = self.assets.get_image("enemy")
        screen_pos = geometry.world_points_to_screen([enemy.get_pos()], hero)[0]
        self.screen.blit(image, screen_pos)

    def draw_hero(self, hero):
        # 현재는 Hero를 화면 하단 중앙의 원으로 표시한다.
        # 나중에 미니맵이나 손/무기 이미지를 추가해도 Renderer 쪽에서 처리하면 된다.
        pygame.draw.circle(
            self.screen,
            "red",
            (int(hero.render_x), int(hero.render_y)),
            int(hero.radius),
        )

    def draw_position_hud(self, hero):
        # 디버깅용 HUD. Hero의 실제 월드 중심 좌표와 HP를 보여준다.
        hero_x, hero_y = hero.get_center()
        position_surface = self.hud_font.render(
            f"x: {hero_x:.0f}  y: {hero_y:.0f}",
            True,
            (235, 235, 245),
        )
        hp_surface = self.hud_font.render(
            f"hp: {hero.life_point:.0f}",
            True,
            (235, 235, 245),
        )

        padding_x = 10
        padding_y = 6
        line_gap = 2
        box_w = max(position_surface.get_width(), hp_surface.get_width()) + padding_x * 2
        box_h = position_surface.get_height() + hp_surface.get_height() + line_gap + padding_y * 2
        box_x = self.screen.get_width() - box_w - 12
        box_y = self.screen.get_height() - box_h - 12
        box = pygame.Rect(box_x, box_y, box_w, box_h)

        pygame.draw.rect(self.screen, (18, 18, 28), box)
        pygame.draw.rect(self.screen, (110, 110, 130), box, 1)
        self.screen.blit(hp_surface, (box_x + padding_x, box_y + padding_y))
        self.screen.blit(
            position_surface,
            (box_x + padding_x, box_y + padding_y + hp_surface.get_height() + line_gap),
        )

    def render(self, hero, walls, enemies):
        # 한 프레임의 출력 순서.
        # 배경 -> 벽 -> 적 -> Hero 표시 -> HUD 순서로 그린다.
        self.clear()

        for wall in walls:
            self.draw_wall(hero, wall)

        for enemy in enemies:
            self.draw_enemy(hero, enemy)

        self.draw_hero(hero)
        self.draw_position_hud(hero)
        pygame.display.flip()
