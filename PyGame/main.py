import os
import sys
import pygame
import time
from pygame import mixer



FPS = 50
pygame.init()
size = WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data/images', name)
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
# flag_image_1 = load_image('animation12.png', colorkey=-1)
# flag_image = pygame.transform.scale(flag_image_1, (150, 40))
# flag = AnimatedSprite(flag_image, 3, 1, 790, 310)
start_animation = AnimatedSprite(load_image('start_animation.png'), 2, 1, 330.5, 367.5)
sound = pygame.mixer.Sound('data\American boy.mp3')
sound.play(-1)


def start_screen():
    # Это функция стартового окна
    fon = pygame.transform.scale(load_image('фон-1.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    while True:
        pygame.display.set_caption('American boy')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # При нажатии на любую клавишу стартовое окно исчезает и появляется игра
                # sound.stop()
                return  # начинаем игру
        all_sprites.update()
        all_sprites.draw(screen)
        clock.tick(4)
        pygame.display.flip()


start_screen()

# Изображение не получится загрузить
# без предварительной инициализации pygame
v = 50
fps = 30
COUNT_LIFE = 3  # глобальная переменная, отвечающая за кол-во жизней у игрока
COUNT_LIFE_START = COUNT_LIFE  # переменная с начальным количеством жизней
FLAG_NEW_LEVEL = False  # переменная отвечающая за переход по уровням
PLATFORM_LEVEL = 0
FLAG_GAME = False  # если жизни заканчиваются, то флаг становится равным True и
# появляется окно с надписью game over
pygame.init()
isCanJump = False    # станет True при нажатии пробела
isJump = False    # для прыжка


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
tile_images = {
    'platform': load_image('platform.png'),
    'portal': load_image('portal.png'),
    'hole': load_image('black_hole.png')
}

tile_width = 60
tile_height = 30


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
            # при встрече с платформой лицом к лицу, в засаде всегда ждет пре-платформа
            # она, подобно черной дыре, отправит на спавн
            super().__init__(tiles_group, all_sprites, hole_group)
            self.image = pygame.Surface((tile_width // 6, tile_height // 2))
            self.image.fill((0, 0, 0))
            self.image.set_colorkey((0, 0, 0))
            self.rect = self.image.get_rect().move(
                tile_width * pos_x + 59, tile_height * pos_y + 470)
        elif tile_type == 'bottom':
            # Нужен для прыжка (был улучшен вечером 17.01.22 и теперь он монолитный)
            super().__init__(tiles_group, all_sprites, platform_group)
            self.image = pygame.Surface((1000, tile_height))
            self.image.fill((0, 0, 0))
            self.image.set_colorkey((0, 0, 0))
            self.rect = self.image.get_rect().move(0, 730)
        #         tile_width * pos_x, tile_height * pos_y)


# image_hero = [load_image('step_1.png'), load_image('step_2.png')]
image_hero = 'hero.png'
jump_hero = 'jump.png'


class Player(pygame.sprite.Sprite):
    global image_hero, jump_hero
    image = load_image(image_hero)

    def __init__(self, group, y):
        # НЕОБХОДИМО вызвать конструктор родительского класса Sprite.
        # Это очень важно !!!
        super().__init__(group)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.velocity = [8, 0]
        self.gravity = 1
        self.rect.x = 0
        self.rect.y = y
        self.change_y = y
        self.flag_collide = False

    # def step(self, step_img):
    #     self.image = step_img

    def update(self, *args):
        global isJump, isCanJump  # для возможности прыжка
        # коллайды:
        on_platform_collide = pygame.sprite.spritecollideany(self, platform_group)  # с платформой
        on_hole_collide = pygame.sprite.spritecollideany(self, hole_group)  # с ч-дырой | пре-платформой
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
            # self.change_y = self.rect.y
        else:
            # problem(1)
            self.velocity[1] += self.gravity  # пока мы в полете, прибавляем гравитацию
        if on_hole_collide:
            # этот условие работает если персонаж наступил на чёрную дыру
            global COUNT_LIFE, fon, fon_past, FLAG_GAME, list_hearts, heart_group, sprite_heart
            self.rect.x = 0  # это возвращает персонажа в начало окна
            COUNT_LIFE -= 1  # это служит счётчиком жизни
            for sprites in heart_group:
                # после попадания в чёрную дыру отнимается одна жизнь
                # для этого все спрайты из группы удаляются и добавляются новые
                sprites.kill()
            length = 0  # x координата спрайта жизни
            for j in range(COUNT_LIFE):
                rect_y = 150
                heart_image = load_image('heart.png')
                heart_image.set_colorkey('white')
                image2 = pygame.transform.scale(heart_image, (90, 70))
                sprite_heart.image = image2
                sprite_heart.rect = sprite_heart.image.get_rect()
                sprite_heart.rect.x = length
                sprite_heart.rect.y = rect_y
                heart_group.add(sprite_heart)
                sprite_heart = pygame.sprite.Sprite()
                length += 60
            if COUNT_LIFE <= 0:
                FLAG_GAME = True
                # если жизни заканчиваются то и игра заканчивается
        if on_portal_collide:
            # данное условие выполняется если персонаж прошел через портал
            global FLAG_NEW_LEVEL  # флаг работает в основном цикле и если он True окно закрывается
            FLAG_NEW_LEVEL = True
        if isCanJump and isJump:
            # это условие необходимо для прыжка.
            # isJump = True при нажатии пробела. isCanJump = True при коллайде с платформой
            isJump, isCanJump = False, False  # а неча по воздуху шпарить прыжками. теперь только до приземления
            self.velocity[1] = -12  # усилие прыжка в 12 антигравитаций
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
heart_group = pygame.sprite.Group()
rect_x = 0
for i in range(COUNT_LIFE):
    # добавляет в группу спрайтов новые спрайты жизней(сердец)
    rect_y = 150
    heart_image = load_image('heart.png')
    heart_image.set_colorkey('white')
    image2 = pygame.transform.scale(heart_image, (90, 70))
    sprite_heart.image = image2
    sprite_heart.rect = sprite_heart.image.get_rect()
    sprite_heart.rect.x = rect_x
    sprite_heart.rect.y = rect_y
    heart_group.add(sprite_heart)
    sprite_heart = pygame.sprite.Sprite()
    rect_x += 60
player = Player(all_sprites, 660)
running = True


def generate_level(level, tile_images):
    # просто функция генерирующая уровень
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


screen.fill((255, 255, 255))
# player, level_x, level_y = generate_level(load_level('map.txt'))
generate_level(load_level('american_boy_map.txt'), tile_images)
running_game_over = True


def game_over():
    # функция, отвечающая за запуск окна game_over
    global running_game_over
    while running_game_over:
        game_over_img = pygame.transform.scale(load_image('game_over.png'), (1000, 800))
        pygame.display.set_caption('American boy')
        screen.fill((0, 0, 0))
        game_over_img.set_colorkey(-1)
        screen.blit(game_over_img, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_game_over = False
                return
        pygame.display.flip()


flag_pause = False


def level(fon):
    # универсальная функция, отвечающая за основной цикл уровня
    # ранее были отдельные функции для прошлого, настоящего и будущего
    # как аргумент в неё подаётся фон времени(настоящее или прошлое или будущее)
    global running, FLAG_NEW_LEVEL, flag_pause, FLAG_GAME
    while running:
        pygame.display.set_caption('American boy')
        screen.blit(fon, (0, 0))
        if FLAG_NEW_LEVEL:
            FLAG_NEW_LEVEL = False  # при попадании в портал появляется новые уровень
            # а флаг вновь становится False
            return
        if FLAG_GAME:
            # если нет жизней, то мы выходим из функции и попадаем на окно game_over
            return
        for event in pygame.event.get():
            screen.blit(fon, (0, 0))
            if event.type == pygame.QUIT:
                running = False
                FLAG_GAME = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not flag_pause:
                    global isJump
                    isJump = True
                    # all_sprites.update('Space')
                if event.key == pygame.K_ESCAPE:
                    # это условие отвечает за паузу при нажатии на клавишу escape
                    if not flag_pause:
                        flag_pause = True  # флаг для паузы
                    else:
                        flag_pause = False
        clock.tick(fps)
        if not flag_pause:
            # если флаг False то персонаж спокойно двигается, и музыка работает
            all_sprites.update()
            pygame.mixer.unpause()
        else:
            # в случае если флаг паузы равен True, мы ставим на паузу не только движения игрока
            # но и саму музыку
            pygame.mixer.pause()
        all_sprites.draw(screen)
        heart_group.draw(screen)
        pygame.display.flip()


level(fon)
if FLAG_GAME:
    running = False
    game_over()

image_hero = 'hero_past.png'
jump_hero = 'jump_past.png'
fon_past = pygame.transform.scale(load_image('Past_location.jpg'), (1000, 800))
screen.blit(fon, (0, 0))
tile_images_past = {
    'platform': load_image('Platform_past.png'),
    'portal': load_image('Portal.png'),
    'hole': load_image('Black_hole.png')
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
generate_level(load_level('american_boy_past.txt'), tile_images_past)
level(fon_past)

if FLAG_GAME:
    game_over()
    running = False

image_hero = 'hero_future.png'
jump_hero = 'jump_future.png'
fon_future = pygame.transform.scale(load_image('Future_location.jpg'), (1000, 800))
screen.blit(fon, (0, 0))
tile_images_future = {
    'platform': load_image('Platform_future.png'),
    'portal': load_image('Portal.png'),
    'hole': load_image('Black_hole.png')
}
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()
hole_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
Player(all_sprites, 670)
screen.fill((255, 255, 255))
generate_level(load_level('american_boy_future.txt'), tile_images_future)
level(fon_future)


if FLAG_GAME:
    game_over()
    running = False

FPS = 50
screen = pygame.display.set_mode(size)
sound.stop()

# финальное окно сделано Иваном Рыжовым


def show_go_screen():
    screen.fill((0, 0, 0))
    pygame.display.flip()
    time.sleep(1)
    bg = load_image("Финальное окно 2 кадр.png")
    screen.blit(bg, (0, 0))
    pygame.display.flip()
    time.sleep(1)
    screen.fill((0, 0, 0))
    pygame.display.flip()
    time.sleep(1)
    bg = load_image("Финальное окно 3 кадр.png")
    screen.blit(bg, (0, 0))
    pygame.display.flip()
    time.sleep(1)
    screen.fill((0, 0, 0))
    pygame.display.flip()
    time.sleep(1)
    bg = load_image("Финальное окно кадр 4.png")
    screen.blit(bg, (0, 0))
    pygame.display.flip()
    time.sleep(1)
    screen.fill((0, 0, 0))
    pygame.display.flip()
    time.sleep(1)
    bg = load_image("Финальное окно кадр 5.png")
    screen.blit(bg, (0, 0))
    pygame.display.flip()
    time.sleep(1)
    screen.blit(bg, (0, 0))
    pygame.display.flip()
    sound = pygame.mixer.Sound('data/anthem.mp3')
    sound.play()

    waiting = True
    while waiting:
        global COUNT_LIFE, COUNT_LIFE_START
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            # if event.type == pygame.KEYUP:
            #     waiting = False
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-01.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-02.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-03.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-04.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-05.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-06.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-07.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-08.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-09.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-10.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-11.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-12.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 90)
        text = font.render(f"ПОТРАЧЕНО {COUNT_LIFE_START - COUNT_LIFE} HP", True, [255, 255, 255])
        screen.blit(text, (250, 650))
        bg = load_image("flag_animation/frame-13.gif")
        screen.blit(bg, (250, 276))
        pygame.display.flip()
        time.sleep(0.3)


if not FLAG_GAME:
    show_go_screen()