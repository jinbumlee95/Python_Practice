import pygame


class InputHandler:
    def __init__(self):
        # 현재 눌려 있는 액션 상태만 저장한다.
        # Hero 같은 게임 객체는 pygame.K_w 같은 키 값을 몰라도 된다.
        self.actions = {
            "forward": False,
            "backward": False,
            "turn_left": False,
            "turn_right": False,
            "strafe_left": False,
            "strafe_right": False,
            "attack": False,
        }

        # pressed_actions 는 KEYDOWN이 들어온 프레임에만 True가 된다.
        # 공격처럼 "꾹 누르는 동안 계속"이 아니라 "한 번 눌렀을 때 한 번" 처리할 때 사용한다.
        self.pressed_actions = {action: False for action in self.actions}
        self.released_actions = {action: False for action in self.actions}
        self.quit_requested = False

        # pygame 키 코드를 게임 액션 이름으로 번역하는 표.
        # 나중에 키 설정을 바꾸고 싶으면 이 dict만 수정하면 된다.
        self.keymap = {
            pygame.K_UP: "forward",
            pygame.K_w: "forward",
            pygame.K_DOWN: "backward",
            pygame.K_s: "backward",
            pygame.K_LEFT: "turn_left",
            pygame.K_a: "turn_left",
            pygame.K_RIGHT: "turn_right",
            pygame.K_d: "turn_right",
            pygame.K_q: "strafe_left",
            pygame.K_e: "strafe_right",
            pygame.K_SPACE: "attack",
            pygame.K_x: "attack",
        }

    def handle_event(self, event):
        # 창 닫기 이벤트도 입력 상태의 일부로 보고, 메인 루프가 나중에 확인하게 한다.
        if event.type == pygame.QUIT:
            self.quit_requested = True
            return

        # 여기서는 키보드 입력만 처리한다. 마우스/패드는 나중에 별도 분기로 추가하면 된다.
        if event.type not in (pygame.KEYDOWN, pygame.KEYUP):
            return

        # 등록되지 않은 키는 게임에서 의미 없는 입력이므로 무시한다.
        action = self.keymap.get(event.key)
        if action is None:
            return

        if event.type == pygame.KEYDOWN:
            # 이미 누르고 있던 키는 새 입력으로 치지 않는다.
            # 그래서 attack 같은 액션이 프레임마다 반복 발동하지 않는다.
            if not self.actions[action]:
                self.pressed_actions[action] = True
            self.actions[action] = True
        elif event.type == pygame.KEYUP:
            self.actions[action] = False
            self.released_actions[action] = True

    def is_pressed(self, action):
        return self.actions.get(action, False)

    def was_pressed(self, action):
        return self.pressed_actions.get(action, False)

    def consume(self, action):
        # 한 번성 입력은 사용한 뒤 False로 돌려서 같은 입력이 중복 처리되지 않게 한다.
        was_pressed = self.was_pressed(action)
        self.pressed_actions[action] = False
        return was_pressed

    def reset_frame(self):
        # 프레임 전용 상태는 매 update가 끝난 뒤 초기화한다.
        # 현재 눌림 상태(actions)는 KEYUP이 올 때까지 유지된다.
        for action in self.pressed_actions:
            self.pressed_actions[action] = False
            self.released_actions[action] = False
