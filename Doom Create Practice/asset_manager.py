from pathlib import Path

import pygame


class AssetManager:
    def __init__(self, base_path=None):
        # pygame 이미지 로드/스케일 처리는 여기서만 맡는다.
        # GameObject는 이미지 객체 대신 크기 정보만 받아서 사용한다.
        self.base_path = Path(base_path or Path(__file__).parent)
        self.images = {}
        self.scaled_images = {}

    def load_image(self, name, relative_path, size=None):
        # 이미지는 프로젝트 폴더 기준 상대 경로로 불러온다.
        image = pygame.image.load(str(self.base_path / relative_path)).convert_alpha()
        if size is not None:
            # 고정 크기로 쓸 이미지는 로드 시점에 한 번만 스케일한다.
            size = tuple(size)
            image = pygame.transform.scale(image, size)
        self.images[name] = image
        return image

    def get_image(self, name):
        return self.images[name]

    def get_scaled_image(self, name, size):
        # 같은 이미지를 같은 크기로 여러 번 요청하면 캐시된 Surface를 재사용한다.
        # 매 프레임 transform.scale을 호출하지 않기 위한 장치다.
        size = tuple(size)
        key = (name, size)
        if key not in self.scaled_images:
            self.scaled_images[key] = pygame.transform.scale(self.images[name], size)
        return self.scaled_images[key]

    def get_size(self, name):
        return self.images[name].get_size()
