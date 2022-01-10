import os
import sys

import pygame
import random

# Изображение не получится загрузить
# без предварительной инициализации pygame
pygame.init()
size = width, height = 1000, 800
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
v = 100
fps = 30
COUNT_LIFE = 3
FLAG_PRESENT = False


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


fon = pygame.transform.scale(load_image('фон-1.png'), (1000, 800))
screen.blit(fon, (0, 0))
tile_images = {
    'platform': load_image('Платформа.png'),
    'portal': load_image('Портал.png'),
    'hole': load_image('Чёрная дыра.png')
}

tile_width = 50
tile_height = 10


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, tile_images):
        if tile_type == 'platform':
            super().__init__(tiles_group, all_sprites, platform_group)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)
        elif tile_type == 'portal':
            super().__init__(tiles_group, all_sprites, portal_group)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)
        elif tile_type == 'hole':
            super().__init__(tiles_group, all_sprites, hole_group)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)
        # else:
        #     super().__init__(tiles_group, all_sprites)
        #     self.image = tile_images[tile_type]
        #     self.rect = self.image.get_rect().move(
        #         tile_width * pos_x, tile_height * pos_y)


image_hero = 'hero.png'
jump_hero = 'jump.png'


class Player(pygame.sprite.Sprite):
    global image_hero, jump_hero
    image = load_image(image_hero)
    # image = [load_image('step_1.png'), load_image('step_2.png')]

    def __init__(self, group, y):
        # НЕОБХОДИМО вызвать конструктор родительского класса Sprite.
        # Это очень важно !!!
        super().__init__(group)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.velocity = [10, -10]
        self.gravity = 1
        self.rect.x = 0
        self.rect.y = y
        self.change_y = y
        self.flag_collide = False

    def update(self, *args):
        # Это if работает, если персонаж наступает на платформу
        if pygame.sprite.spritecollideany(self, platform_group):
            block_hit_list = pygame.sprite.spritecollide(self, platform_group, False)
            for block in block_hit_list:
                self.rect.bottom = block.rect.top  # это делает высоту персонажа равной
                # высоте платформы
                self.image = load_image(image_hero)
                # здесь меняется изображение с прыжка на обычное
                self.change_y = self.rect.y
        if pygame.sprite.spritecollideany(self, hole_group):
            # этот условие работает если персонаж наступил на чёрную дыру
            global COUNT_LIFE
            self.rect.x = 0  # это возвращает персонажа в начало окна
            COUNT_LIFE -= 1  # это служит счётчиком жизни
        if pygame.sprite.spritecollideany(self, portal_group):
            # данное условие выполняется если персонаж зашёл на портал
            global FLAG_PRESENT  # флаг работает в основном цикле и если он True окно закрывается
            FLAG_PRESENT = True
        if args == ('Space',) or self.rect.y < self.change_y:
            # это условие необходимо для прыжка и возвращения персонажа на землю после прыжка
            if not pygame.sprite.spritecollideany(self, platform_group):
                self.change_y = 670  # это будет высотой на которой ходит персонаж по земле
            # self.change_y = 670
            self.image = load_image(jump_hero)  # тут обычное изображение меняется на изображение прыжка
            # ниже код для гравитации и скорости
            self.velocity[1] += self.gravity
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
        else:
            # в этой части персонажу задаётся обычная картинка, скорость и постоянно увеличивается его координата по x
            self.image = load_image(image_hero)
            self.velocity = [10, -10]
            self.rect.x += 4
            # self.image = load_image('step_2.png')


tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()
hole_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
sprite_heart = pygame.sprite.Sprite()
# heart_image = load_image('heart.png', colorkey=-1)
# image2 = pygame.transform.scale(heart_image, (300, 100))
# sprite_heart.image = image2
# sprite_heart.rect = sprite_heart.image.get_rect()
# sprite_heart.rect.x = 400
# sprite_heart.rect.y = 400
# all_sprites.add(sprite_heart)
Player(all_sprites, 670)
running = True


def generate_level(level, tile_images):
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('platform', x, 70, tile_images)
            elif level[y][x] == '@':
                Tile('portal', x, 64, tile_images)
            elif level[y][x] == 'H':
                Tile('hole', x, 70, tile_images)


screen.fill((255, 255, 255))
# player, level_x, level_y = generate_level(load_level('map.txt'))
generate_level(load_level('american_boy_map.txt'), tile_images)
running_past = True


def present():
    global running, FLAG_PRESENT, running_past
    while running:
        pygame.display.set_caption('American boy')
        screen.blit(fon, (0, 0))
        # внутри игрового цикла ещё один цикл
        # приема и обработки сообщений
        for event in pygame.event.get():
            # при закрытии окна
            if FLAG_PRESENT:
                FLAG_PRESENT = False
                return
            if event.type == pygame.QUIT:
                running = False
                running_past = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    all_sprites.update('Space')
        clock.tick(fps)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()


present()

image_hero = 'hero_past.png'
jump_hero = 'jump_past.png'
fon_past = pygame.transform.scale(load_image('Past_location.jpg'), (1000, 800))
screen.blit(fon, (0, 0))
tile_images_past = {
    'platform': load_image('Platform_past.png'),
    'portal': load_image('Портал.png'),
    'hole': load_image('Чёрная дыра.png')
}
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()
hole_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
Player(all_sprites, 670)
# running = True
screen.fill((255, 255, 255))
# player, level_x, level_y = generate_level(load_level('map.txt'))
generate_level(load_level('american_boy_past.txt'), tile_images_past)


def past():
    global running, FLAG_PRESENT
    while running:
        pygame.display.set_caption('American boy')
        screen.blit(fon_past, (0, 0))
        # внутри игрового цикла ещё один цикл
        # приема и обработки сообщений
        for event in pygame.event.get():
            # при закрытии окна
            if FLAG_PRESENT:
                return
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    all_sprites.update('Space')
        clock.tick(fps)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()


past()