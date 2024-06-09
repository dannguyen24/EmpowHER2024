import pygame

class Button:
    def __init__(self, text, position, font, text_color, bg_color,  width, height):
        self.width = width
        self.height = height
        self.box_color = bg_color
        self.text_object = font.render(text, True, text_color)
        self.text_rect = self.text_object.get_rect(center=position)
        self.answer = text
        self.clicked = False
        self.x_pos = 0
        self.y_pos = 0
        self.choice_box = None
        self.active = False

    def draw(self, window, x, y):
        self.choice_box = pygame.Rect(x, y, self.width, self.height)
        # draw button on screen
        pygame.draw.rect(window, self.box_color, self.choice_box)
        window.blit(self.text_object, self.text_rect)
        self.x_pos = x
        self.y_pos = y

    def press_button(self):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()

        # Check mouseover and clicked conditions
        if self.choice_box.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action

    def set_bg_color(self, bg_color):
        self.box_color = bg_color





