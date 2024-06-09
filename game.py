import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5
FONT = pygame.font.SysFont("Arial", 30)
QUIZ_COLOR = "#6DA4AA"
CHOICE_COLOR = "#647D87"
RED = "#BF3131"
GREEN = "#0A6847"
index = 0
pygame.display.set_caption("New game")
window = pygame.display.set_mode((WIDTH, HEIGHT))
class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()

        self.game_state_manager = GameStateManager('normal')
        self.normal = Normal(window, self.game_state_manager)
        self.quiz = Quiz(window, self.game_state_manager)
        self.states = {'normal': self.normal, 'quiz': self.quiz}

    def run(self):
        background, bg_image = get_background("Blue.png")

        block_size = 96

        player = Player(220, HEIGHT - block_size - 64, 50, 50)
        # Set up fire
        fire = Fire(450, HEIGHT - block_size - 64, 16, 32)
        fire.on()
        # Set up start flag
        start_pos = 100
        start_flag = Start_flag(start_pos, HEIGHT - block_size - 64 * 2, 64, 64)
        start_flag.moving()
        # Set up finish flag
        finish_pos = WIDTH * 2 - block_size - 64 * 2
        print("finish flag pos: " + str(WIDTH * 2 - block_size - 64 * 2))
        finish_flag = Finish_flag(finish_pos, HEIGHT - block_size - 64 * 2, 64, 64)
        finish_flag.moving()
        # Set up Questions
        question_point = Question_point(500, HEIGHT - block_size - 64, 32, 64)
        question_point.idle()
        # Set up floor
        floor = [Block(i * block_size, HEIGHT - block_size, block_size)
                 for i in range(-WIDTH // block_size, (WIDTH * 3) // block_size)]
        objects = [*floor, start_flag, finish_flag, question_point]

        offset_x = 0
        scroll_area_width = 500

        while True:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and player.jump_count < 2:
                        player.jump()

            self.states[self.game_state_manager.get_state()].run(window, player, fire, start_flag, finish_flag,background, bg_image, objects, offset_x)

            if (player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0 and (
                    offset_x + scroll_area_width + 200 <= finish_pos):
                offset_x += player.x_vel
            elif (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0 and (
                    offset_x + scroll_area_width >= start_pos):
                offset_x += player.x_vel

            pygame.display.update()
            #self.clock.tick(FPS)

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.score = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    #Animating the Player
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

#Adding Terrains and Blocks
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

#Add check_point
class Question_point(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "qPoint")
        self.question_point = load_sprite_sheets("Items", "Questions", width, height)
        self.image = self.question_point["question_point"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "question_point"

    def idle(self):
        self.animation_name = "question_point"

    def press(self):
        self.animation_name = "question_point"

    def loop(self):
        sprites = self.question_point[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

#Add start flag
class Start_flag(Object):
    ANIMATION_DELAY = 17
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "startFlag")
        self.start_flag = load_sprite_sheets("Items", "Start", width, height)
        self.image = self.start_flag["startIdle"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "startIdle"

    def idle(self):
        self.animation_name = "startIdle"

    def moving(self):
        self.animation_name = "startMoving"

    def loop(self):
        sprites = self.start_flag[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

#Add finish flag
class Finish_flag(Object):
    ANIMATION_DELAY = 8

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "finishFlag")
        self.finish_flag = load_sprite_sheets("Items", "End", width, height)
        self.image = self.finish_flag["endIdle"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "endIdle"

    def idle(self):
        self.animation_name = "endIdle"

    def moving(self):
        self.animation_name = "endPressed"

    def loop(self):
        sprites = self.finish_flag[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
    def get_state(self):
        return self.currentState
    def set_state(self, currentState):
        print("This is set state")
        self.currentState = currentState

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

#Temporary
quiz_data = {
        "questions": "What do we call the most basic structural unit of living things?",
        "choices": ["DNA", "Cell"],
        "ans": "Cell"
    }
def draw_quiz(window):
    print("draw quiz now")
    current_question = list(quiz_data.values())[0]
    current_answer = list(quiz_data.values())[2]
    current_question_object = FONT.render(current_question, True, "white")
    current_question_rect = current_question_object.get_rect(center=(500,200))
    current_index_object = FONT.render(f"{index+1}/{len(quiz_data)}", True, "white")

    # Set rectangle dimensions and position
    question_rect_width = 800  # Adjust these values as needed
    question_rect_height = 600
    box = pygame.Rect((WIDTH - question_rect_width) // 2, (HEIGHT - question_rect_height) // 2, question_rect_width,
                      question_rect_height)
    pygame.draw.rect(window, QUIZ_COLOR, box)
    window.blit(current_question_object, current_question_rect)

    #Set choices
    list_of_choices = list(quiz_data.values())[1]
    rendered_choices = []
    for choice in list_of_choices:
        rendered_choices.append(FONT.render(choice, True, "white"))

    positions = [(295, 400), (705, 400), (295, 550), (705, 550)]
    choice_rect = [choice.get_rect(center=pos) for pos, choice in zip(positions, rendered_choices)]

    choice_rect_width = 350
    choice_rect_height = 100
    choice_boxes = []
    for i in range(4):  # Assuming 4 choices
        # Calculate centered x-coordinate based on choice_rect_width
        if i % 2 == 0:
            x_pos = (WIDTH - question_rect_width) // 2 + 20
        else:
            x_pos = 530

        if i == 0 or i == 1:
            y_pos = (HEIGHT - choice_rect_height) // 2
        else:
            y_pos = (HEIGHT - choice_rect_height) // 2 + 150

        choice_boxes.append(pygame.Rect(x_pos, y_pos, choice_rect_width, choice_rect_height))

    for box in choice_boxes:
        pygame.draw.rect(window, CHOICE_COLOR, box)

    for obj, rect in zip(rendered_choices, choice_rect):
        window.blit(obj, rect)

    pygame.display.update()

    return current_answer, choice_boxes

def answer_question():
    mouse = pygame.mouse.get_pressed()[0]
    answer, choice_boxes = draw_quiz(window)
    #if mouse and :
        #if


def handle_move(player, objects, game_state_manager):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
        elif obj and obj.name == "finishFlag":
            print("IT finishes")
        # Set up question
        elif obj and obj.name == "qPoint":
            if keys[pygame.K_f]:
                print("press f")
                game_state_manager.set_state('quiz')


#When reach the finishing line
def winner(player):
    player.move(0,0)

class Quiz:
    def __init__(self, display, game_state_manager):
        self.display = display
        self.game_state_manager = game_state_manager
        self.correct_answer = False
    def run(self, window,  player, fire, start_flag, finish_flag,background, bg_image, objects, offset_x):
        self.display.fill('#FF9843')
        answer_question()

class Normal:
    def __init__(self, display, game_state_manager):
        self.display = display
        self.game_state_manager = game_state_manager

    def run(self, window, player, fire, start_flag, finish_flag,background, bg_image, objects, offset_x):
        player.loop(FPS)
        fire.loop()
        start_flag.loop()
        finish_flag.loop()
        handle_move(player, objects, self.game_state_manager)
        draw(window, background, bg_image, player, objects, offset_x)

if __name__ == "__main__":
    game = Game()
    game.run()