import random
import pygame
import os
import sys
from pygame import mixer


FPS = 50

pygame.init()
size = WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


all_sprites = pygame.sprite.Group()
sprite = pygame.sprite.Sprite()
flag_image_1 = load_image('animation12.png', colorkey=-1)
flag_image = pygame.transform.scale(flag_image_1, (150, 40))
flag = AnimatedSprite(flag_image, 3, 1, 790, 310)
start_animation = AnimatedSprite(load_image('start_animation.png'), 2, 1, 330.5, 367.5)


def start_screen():
    fon = pygame.transform.scale(load_image('фон-1.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    sound = pygame.mixer.Sound('American boy.mp3')
    sound.play(-1)
    while True:
        pygame.display.set_caption('American boy')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
            flag.update()
        all_sprites.update()
        all_sprites.draw(screen)
        clock.tick(4)
        pygame.display.flip()

start_screen()