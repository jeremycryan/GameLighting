import pygame
import numpy as np
from math import sqrt
from constants import *

class Player():
    def __init__(self, id_num, color, control_scheme, pos):
        self.id = id_num
        self.color = color
        self.control_scheme = control_scheme
        self.pos = pos
        self.vel = [0, 0]

        self.accel_constant = 6
        self.friction_constant = 0.8

        self.brightness = 1.0

    def check_movement(self):
        presses = self.test_keypresses()
        ax = float(presses[3] - presses[1])
        ay = float(presses[2] - presses[0])
        (ax, ay) = (ax / max(np.linalg.norm((ax, ay)), 1) * self.accel_constant,
                    ay / max(np.linalg.norm((ax, ay)), 1) * self.accel_constant)
        self.vel[0] += ax
        self.vel[1] += ay
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[0] = self.vel[0] * self.friction_constant
        self.vel[1] = self.vel[1] * self.friction_constant

    def test_keypresses(self):
        control_presses = []
        pygame.event.pump()
        key_presses = pygame.key.get_pressed()
        for item in self.control_scheme:
            control_presses.append(key_presses[item])
        return control_presses

class Obstacle():
    def __init__(points):
        self.points = np.asarray(shape)

    def determine_shadow(self, pos):
        angles = []
        shadow_points = []
        for item in self.points:
            angle_off = atan2(-(item[1] - pos[1]), item[0] - pos[0])
            angles.append(angle_off)
        a = np.argmin(angles)
        b = np.argmin(angles)
        shadow_points.append(self.points[a], self.points[b])





class ControlScheme():
    def __init__(self, directions):
        self.directions = directions    #   Should be array of keys

class Display():
    def __init__(self):
        self.screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
        self.board = np.zeros((WINDOW_WIDTH, WINDOW_HEIGHT, 3))

    def clear_screen(self, color = (0, 0, 0)):
        self.screen.fill((color))
        self.clear_board()

    def render_light(self, color, origin_pos, pos_list, max_intensity = 1.0):
        mult = 1
        diffs = pos_list - origin_pos
        dists = (diffs[:, 0]**2 + diffs[:, 1]**2)**-0.2*mult
        self.board = self.board.reshape(WINDOW_WIDTH*WINDOW_HEIGHT, 3)
        print self.board.shape
        self.board += np.asarray([dists]*3).transpose() * np.asarray(color)
        self.board = np.reshape(self.board, (WINDOW_WIDTH, WINDOW_HEIGHT, 3))
        surf = pygame.surfarray.make_surface(self.board)
        return surf

    def commit_renders(self, surf):
        self.screen.blit(surf, (0, 0))

    def clear_board(self):
        self.board = np.zeros((WINDOW_WIDTH, WINDOW_HEIGHT, 3))

class Game():
    def __init__(self):
        pygame.init()
        pygame.display.init()

        self.disp = Display()

        self.players = []

    def run(self):
        self.disp.clear_screen()

        player_1_control = [pygame.K_UP,
                            pygame.K_LEFT,
                            pygame.K_DOWN,
                            pygame.K_RIGHT]
        player_1_color = PLAYER_COLORS[0]
        player_1 = Player(1, player_1_color, player_1_control, [0, 0])

        player_2_control = [pygame.K_w,
                            pygame.K_a,
                            pygame.K_s,
                            pygame.K_d]
        player_2_color = PLAYER_COLORS[1]
        player_2 = Player(2, player_2_color, player_2_control, [WINDOW_WIDTH, WINDOW_HEIGHT])
        self.players.append(player_1)
        self.players.append(player_2)

        self.pos_list = []
        for x in range(WINDOW_WIDTH):
            for y in range(WINDOW_HEIGHT):
                self.pos_list.append([x, y])
        self.pos_list = np.asarray(self.pos_list)

        while True:
            self.disp.clear_screen()
            for player in self.players:
                player.check_movement()
                a = self.disp.render_light(player.color,
                                        player.pos,
                                        self.pos_list)
            self.disp.commit_renders(a)
            pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.run()
