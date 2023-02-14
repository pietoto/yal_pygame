import random

import pygame

pygame.init()

width = 800
height = 600
screen = pygame.display.set_mode((width, height))

fps = 60
clock = pygame.time.Clock()

font_path = 'ofont.ru_Balkara Condensed.ttf'  # добавление кастомного текста
font_large = pygame.font.Font(font_path, 48)
font_small = pygame.font.Font(font_path, 24)

game_over = False
retry_text = font_small.render('PRESS ANY KEY', True, (255, 255, 255))  # текст во время рестарта игры
retry_rect = retry_text.get_rect()
retry_rect.midtop = (width // 2, height // 2)

player_ground_image = pygame.image.load('map_2.png')  # пол
player_ground_image = pygame.transform.scale(player_ground_image, (804, 60))
player_ground_height = player_ground_image.get_height()

enemy_image = pygame.image.load('en_2.png')  # враг
enemy_image = pygame.transform.scale(enemy_image, (80, 80))

enemy_killed = pygame.image.load('killed_ghost.png')  # анимация смерти  врага
enemy_killed = pygame.transform.scale(enemy_killed, (80, 80))

player_image = pygame.image.load('pl_3.png')  # колдунчик
player_image = pygame.transform.scale(player_image, (60, 80))


class Entity:  # класс сущности
    def __init__(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.x_speed = 0  # скорость по x
        self.y_speed = 0  # скорость по y
        self.speed = 5
        self.is_out = False
        self.is_dead = False
        self.jump_speed = -12
        self.gravity = 0.5
        self.is_on = False

    def player_hand(self):  # ввод пользователем
        pass

    def kill(self, killed_image):  # мёртвая сущность
        self.image = killed_image
        self.is_killed = True
        self.x_speed = - self.x_speed
        self.y_speed = self.jump_speed
        self.is_out = True

    def update(self):
        self.rect.x += self.x_speed
        self.y_speed += self.gravity
        self.rect.y += self.y_speed

        if self.is_dead:
            if self.rect.top > height - player_ground_height:
                self.is_out = True
        else:
            self.player_hand()

            if self.rect.bottom > height - player_ground_height:
                self.is_on = True
                self.y_speed = 0
                self.rect.bottom = height - player_ground_height

    def drawing(self, surface):  # рисунок
        surface.blit(self.image, self.rect)


class Player(Entity):  # класс игрока
    def __init__(self):
        super().__init__(player_image)
        self.respawn()

    def player_hand(self):
        self.x_speed = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # движение героя влево
            self.x_speed = -self.speed

        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:  # движение героя вправо
            self.x_speed = self.speed

        if self.is_on and (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[
            pygame.K_w]):  # проверка на то, стоит ли герой на земле
            self.is_on = False
            self.jump()

    def jump(self):
        self.y_speed = self.jump_speed

    def respawn(self):  # появление игрока
        self.is_out = False
        self.is_dead = False
        self.rect.midbottom = (width // 2, height - player_ground_height)


class Monster(Entity):  # класс приведения
    def __init__(self):
        super().__init__(enemy_image)
        self.spawn()

    def spawn(self):
        direction = random.randint(0, 1)

        if direction == 0:
            self.x_speed = self.speed
            self.rect.bottomright = (0, 0)

        else:
            self.x_speed = -self.speed
            self.rect.bottomleft = (width, 0)

    def update(self):
        super().update()
        if self.x_speed > 0 and self.rect.left > width or self.x_speed < 0 and self.rect.right < 0:
            self.is_out = True


player = Player()
score = 0

monsters = []
delay = 2000
spawn_delay = delay  # задержка между появлениями монстров
decrease_spawn = 1.01  # уменьшение разницы между появлениями
spawn_ = pygame.time.get_ticks()  # задержка в самом начале

start = True  # меню для игры
while start:

    start_background = pygame.image.load('menu_.jpg')
    screen.blit(start_background, (0, 0))

    font = pygame.font.Font(None, 50)

    text = font.render("    Press to play   ", True, pygame.Color('#78a2b7')) # старт игры
    text_x = width // 2 - text.get_width() // 2
    text_y = height // 2 - text.get_height() // 2 - 100
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.display.flip()
    t = True

    while t:
        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                quit()

            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                start = False
                t = False

running = True  # игра
while running:

    for element in pygame.event.get():

        if element.type == pygame.QUIT:
            running = False

        elif element.type == pygame.KEYDOWN:
            if player.is_out:
                score = 0
                spawn_delay = delay
                spawn_ = pygame.time.get_ticks()
                player.respawn()
                monsters.clear()

    clock.tick(fps)
    screen.fill((54, 207, 232))

    screen.blit(player_ground_image, (0, height - player_ground_height))
    score_text = font_large.render(str(score), True, (255, 255, 255))
    score_rect = score_text.get_rect()

    if player.is_out:
        score_rect.midbottom = (width // 2, height // 2)
        screen.blit(retry_text, retry_rect)

    else:
        player.update()
        player.drawing(screen)

        time_n = pygame.time.get_ticks()
        elapsed = time_n - spawn_

        if elapsed > spawn_delay:
            spawn_ = time_n
            monsters.append(Monster())

        for monster in list(monsters):

            if monster.is_out:
                monsters.remove(monster)

            else:
                monster.update()
                monster.drawing(screen)

            if not player.is_dead and not monster.is_dead and player.rect.colliderect(monster.rect):

                if player.rect.bottom - player.y_speed < monster.rect.top:

                    monster.kill(enemy_killed)
                    player.jump()
                    score += 1  # увелечение счёта после убийства монстра
                    spawn_delay = delay / (decrease_spawn ** score)  # ускорения появления монстров

                else:
                    player.kill(player_image)

        score_rect.midtop = (width // 2, 5)

    screen.blit(score_text, score_rect)
    pygame.display.flip()

quit()
