# code set up
# os use for loading images
import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()
# pygame.display.set_caption sets the game window title. 
pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 60    # frame per second
PLAYER_VEL = 5  # player velocity

#pygame.display.set_mode sets the window size.
window = pygame.display.set_mode((WIDTH, HEIGHT))


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


def handle_move(player, objects):
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
                print("This is the question")


#When reach the finishing line
def winner(player):
    player.move(0,0)

# Main function
    
class QuestionBox:
    def __init__(self, question, correct_answer):
        self.question = question
        self.correct_answer = correct_answer
        self.answer = ""

    def display(self):
        # display the question box and take input for the answer
        #  print the question and take input from the console
        print("Question:", self.question)
        self.answer = input("Your answer: ")

    def check_answer(self):
        # Check if the given answer matches the correct answer
        return self.answer.strip().lower() == self.correct_answer.lower()
def display_question(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

    # while not done:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #             exit()
            # if event.type == pygame.MOUSEBUTTONDOWN:
            #     if input_box.collidepoint(event.pos):
            #         active = not active
            #     else:
            #         active = False
            #     color = color_active if active else color_inactive
            # if event.type == pygame.KEYDOWN:
            #     if active:
            #         if event.key == pygame.K_RETURN:
            #             return text
            #         elif event.key == pygame.K_BACKSPACE:
            #             text = text[:-1]
            #         else:
                        text += event.unicode

        window.fill((0, 0, 0))  # Clear the screen with black
        question_surface = font.render(question, True, pygame.Color('white'))
        window.blit(question_surface, (WIDTH // 2 - question_surface.get_width() // 2, HEIGHT // 2 - 50))
        
        txt_surface = font.render(text, True, color)
        width = max(300, txt_surface.get_width() + 10)
        input_box.w = width
        window.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(window, color, input_box, 2)

        pygame.display.flip()
        pygame.time.Clock().tick(30)
# Câu hỏi
questions = [
    ("Đơn vị cơ bản của sự sống là gì?", "Tế bào"),
    ("Cấu trúc nào kiểm soát sự ra vào của các chất trong tế bào?", "Màng tế bào"),
    ("Quá trình quang hợp diễn ra ở đâu trong tế bào thực vật?", "Lục lạp"),
    ("Bào quan nào được gọi là nhà máy điện của tế bào?", "Ty thể"),
    ("Bào quan nào chịu trách nhiệm tổng hợp protein?", "Ribosome"),
    ("Cấu trúc nào chứa vật liệu di truyền của tế bào?", "Nhân"),
    ("Chất giống như thạch bên trong tế bào là gì?", "Tế bào chất"),
    ("Cấu trúc nào giúp duy trì hình dạng và hỗ trợ tế bào?", "Khung tế bào"),
    ("Bào quan nào tiêu hóa và phân giải chất thải trong tế bào động vật?", "Lysosome"),
    ("Quá trình tế bào phân chia được gọi là gì?", "Phân chia tế bào"),
]

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(220, HEIGHT - block_size - 64, 50, 50)
    
    #Set up fire
    fire = Fire(450, HEIGHT - block_size - 64, 16, 32)
    fire.on()

    #Set up start flag
    start_pos = 100
    start_flag = Start_flag(start_pos, HEIGHT - block_size - 64 * 2, 64, 64)
    start_flag.moving()

    #Set up finish flag
    finish_pos = WIDTH * 2 - block_size - 64 * 2
    print("finish flag pos: " + str(WIDTH * 2 - block_size - 64 * 2))
    finish_flag = Finish_flag(finish_pos, HEIGHT - block_size - 64 * 2, 64, 64)
    finish_flag.moving()

    #Set up Questions
    question_point = Question_point(600, HEIGHT - block_size - 64, 32, 64)
    question_point.idle()
    #Set up floor
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 3) // block_size)]
    objects = [*floor, fire, start_flag, finish_flag, question_point]

    offset_x = 0
    scroll_area_width = 500

    question = QuestionBox("What is 2 + 2?", "4")  # Example question
    question_displayed = False

    run = True
    while run:
        clock.tick(FPS)
        # Checking for inputing event
        direction = 0  
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    direction = 1
                if event.key == pygame.K_LEFT:
                    direction = -1
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                if pygame.sprite.collide_rect(player, question_point):
                    # Display question box only if not already displayed
                    if not question_displayed:
                        display_question(window, questions[0])
                        question_displayed = True
                        # Check the answer

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    direction = 0
                if event.key == pygame.K_LEFT:
                    direction = 0

        
        player.loop(FPS)
        fire.loop()
        start_flag.loop()
        finish_flag.loop()
        
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0 and offset_x + scroll_area_width + 200 <= finish_pos):
            offset_x += player.x_vel
        elif (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0 and offset_x + scroll_area_width >= start_pos:
            offset_x += player.x_vel


        print(offset_x)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)