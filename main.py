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
isCanJump = False    # для прыжка
isJump = False    # станет True при нажатии пробела
v = 100
jumpulse = 12
gravity = 1
fps = 60
COUNT_LIFE = 3
FLAG_PRESENT = False


def load_image(name, colorkey=None):
    fullname = os.path.join('data\images', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_level(filename):
    filename = "data/locations/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


fon = pygame.transform.scale(load_image('фон-1.png'), (1000, 800))
screen.blit(fon, (0, 0))

tile_width = 60    # стандартные
tile_height = 30    # размеры тайлов

tile_images = {
    'platform': load_image('platform.png'),
    'portal': load_image('portal.png'),
    'hole': load_image('black_hole.png')
}    # некоторые тайлы имеют личный pygame.Surface и им нет дела до загрузки каких-то картинок


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, tile_images):
        if tile_type == 'platform':
            super().__init__(tiles_group, all_sprites, platform_group)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y + 460)
        elif tile_type == 'portal':
            super().__init__(tiles_group, all_sprites, portal_group)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y + 400)
        elif tile_type == 'hole':
            super().__init__(tiles_group, all_sprites, hole_group)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y + 460)
        elif tile_type == 'pre-platform':
            # при встрече с платформой лицом к лицу, в засаде всегда ждет пре-пратформа
            # она, подобно черной дыре, отправит на спавн
            super().__init__(tiles_group, all_sprites, hole_group)
            self.image = pygame.Surface((tile_width // 6, tile_height // 2))
            self.image.fill((0, 0, 0))
            self.image.set_colorkey((0, 0, 0))
            self.rect = self.image.get_rect().move(
                tile_width * pos_x + 59, tile_height * pos_y + 465)
        elif tile_type == 'bottom':
            # Нужен для прыжка (был улучшен вечером 17.01.22 и теперь он монолитный)
            super().__init__(tiles_group, all_sprites, platform_group)
            self.image = pygame.Surface((1000, tile_height))
            self.image.fill((0, 0, 0))
            # self.image.set_colorkey((0, 0, 0))
            self.rect = self.image.get_rect().move(0, 730)
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
        self.velocity = [8, 0]
        self.gravity = gravity
        self.rect.x = 0
        self.rect.y = y
        self.flag_collide = False

    def update(self):
        global isJump, isCanJump  # для возможности прыжка
        # коллайды:
        on_platform_collide = pygame.sprite.spritecollideany(self, platform_group)  # с платформой
        on_hole_collide = pygame.sprite.spritecollideany(self, hole_group)    # с ч-дырой | пре-платформой
        on_portal_collide = pygame.sprite.spritecollideany(self, portal_group)  # с порталом
        if on_platform_collide:
            # коллайдимся с платформой, а значит:
            block_hit_list = pygame.sprite.spritecollide(self, platform_group, False)
            block = block_hit_list[0]
            if self.rect.bottom <= block.rect.top + tile_height // 2:
                # значит удар пришелся не на голову. череп не поврежден
                self.velocity[1] = 0  # ниже пола нам падать не надо, верт. скорость обнуляется
                isCanJump = True  # теперь можно прыгнуть, нужно лишь нажать на большую прямоугольную кнопку без текста
                self.image = load_image(image_hero)  # стоим на земле и загружаем обычную картинку
            elif self.rect.top >= block.rect.bottom - tile_height // 2:
                # самому становится больно, когда понимаешь, как он шибанулся об платформу
                self.velocity[1] = self.gravity * 2
            # высоте платформы
            #self.change_y = self.rect.y
        else:
            # problem(1)
            self.velocity[1] += self.gravity  # пока мы в полете, прибавляем гравитацию
        if on_hole_collide:
            # этот условие работает если персонаж угодил в чёрную дыру | пре-платформу
            global COUNT_LIFE
            self.rect.x = 0  # это возвращает персонажа в начало окна
            COUNT_LIFE -= 1  # это служит счётчиком жизни
        if on_portal_collide:
            # данное условие выполняется если персонаж прошел через портал
            global FLAG_PRESENT  # флаг работает в основном цикле и если он True окно закрывается
            FLAG_PRESENT = True
        if isCanJump and isJump:
            # это условие необходимо для прыжка.
            # isJump = True при нажатии пробела. isCanJump = True при коллайде с платформой
            isJump, isCanJump = False, False  # а неча по воздуху шпарить прыжками. теперь только до приземления
            self.velocity[1] = -jumpulse    # прыжок силой в jumpulse
            self.image = load_image(jump_hero)  # тут изображение меняется на изображение прыжка
        self.rect.x += self.velocity[0]  # тут мы по сути просто обновляем позицию
        self.rect.y += self.velocity[1]  # игрока с учетом x,y скоростей


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
Player(all_sprites, 660)
running = True


def generate_level(level, tile_images):
    for tile in tiles_group:
        tile.kill()
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('platform', x, y, tile_images)
            elif level[y][x] == '@':
                Tile('portal', x, y, tile_images)
            elif level[y][x] == 'H':
                Tile('hole', x, y, tile_images)
            elif level[y][x] == '<':
                Tile('pre-platform', x, y, tile_images)
            elif level[y][x] == '-':
                Tile('bottom', x, y, tile_images)


#screen.fill((255, 255, 255))
# player, level_x, level_y = generate_level(load_level('map.txt'))
generate_level(load_level('location.txt'), tile_images)
running_past = False


def present():
    pygame.display.set_caption('American boy')
    global running, FLAG_PRESENT
    while running:
        screen.blit(fon, (0, 0))
        if FLAG_PRESENT:
            FLAG_PRESENT = False
            return
        # внутри игрового цикла ещё один цикл
        # приема и обработки сообщений
        for event in pygame.event.get():
            # при закрытии окна
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    global isJump
                    isJump = True
                    # all_sprites.update('Space')
        clock.tick(fps)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()


present()

image_hero = 'hero_past.png'
jump_hero = 'jump_past.png'
fon_past = pygame.transform.scale(load_image('фон-2.jpg'), (1000, 800))
screen.blit(fon, (0, 0))
tile_images_past = {
    'platform': load_image('platform_past.png'),
    'portal': load_image('portal.png'),
    'hole': load_image('black_hole.png')
}    # когда-то в давным-давно некоторые тайлы знали лишь pygame.Surface и даже не подозревали о картинках
'''
tiles_group = pygame.sprite.Group()      # не уверен, что оно вообще тут нужно второй раз
player_group = pygame.sprite.Group()     # мы уже задали это ранее
platform_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()
hole_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
'''
Player(all_sprites, 660)
running = True
#screen.fill((255, 255, 255))
# player, level_x, level_y = generate_level(load_level('map.txt'))
generate_level(load_level('location_past.txt'), tile_images_past)


def past():
    pygame.display.set_caption('American boy in past')
    global running, FLAG_PRESENT
    while running:
        screen.blit(fon_past, (0, 0))
        if FLAG_PRESENT:
            return
        # внутри игрового цикла ещё один цикл
        # приема и обработки сообщений
        for event in pygame.event.get():
            # при закрытии окна
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    global isJump
                    isJump = True
                    # all_sprites.update('Space')
        clock.tick(fps)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()


past()