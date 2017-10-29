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

        self.accel_constant = 8
        self.friction_constant = 0.7

        self.brightness = 1.0
        self.min_brightness = 0.2

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

    def check_brightness(self):
        presses = self.test_keypresses()
        self.brightness = max(self.min_brightness, self.brightness - (self.brightness - max(presses))/7)

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
        self.screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen_commit = pygame.display.set_mode([DISPLAY_WIDTH, DISPLAY_HEIGHT])
        self.board = np.zeros((WINDOW_WIDTH, WINDOW_HEIGHT, 3))
        self.clock = pygame.time.Clock()

    def clear_screen(self, color = (0, 0, 0)):
        self.screen.fill((color))
        self.clear_board()

    def add_shadows(self, diffs, dists, obstacles):
        for obstacle in obstacles:

            #   Determine which pixels are in a cone with obstacle
            v1 = obstacle[0]/np.linalg.norm(obstacle[0])
            v2 = obstacle[1]/np.linalg.norm(obstacle[1])
            vs = np.asarray([v1, v2]).transpose()
            vd = np.linalg.solve(vs, diffs.transpose()).transpose()
            vd[:, 0] = -np.clip(vd[:, 0]*100, 0, 1) + 1
            vd[:, 1] = -np.clip(vd[:, 1]*100, 0, 1) + 1
            vd = vd[:, 0] + vd[:, 1]

            #   Determine which pixels are past the wall
            rel_diffs = diffs - obstacle[0]
            rel_obstacle = obstacle - obstacle[0]
            unit_norm = np.matmul(np.asarray([[0, -1], [1, 0]]),
                rel_obstacle[1]/np.linalg.norm(rel_obstacle))
            dist_behind_wall = np.matmul(rel_diffs, unit_norm)
            is_behind_wall = np.clip(dist_behind_wall, 0, 1)

            player_is_behind_wall = np.matmul(-obstacle[0], unit_norm)

            if np.sign(player_is_behind_wall) == 1:
                vd += is_behind_wall
            else:
                vd += 1-is_behind_wall

            dists *= np.clip(vd, 0, 1)
        return dists

    def render_light(self, color, origin_pos, pos_list, obstacles, max_intensity = 1.0):
        pervasiveness = 20
        mult = 0.7
        diffs = pos_list - origin_pos
        dists = (diffs[:, 0]**2 + diffs[:, 1]**2)**0.5+2
        dists = (dists/pervasiveness)**-1*mult
        dists = self.add_shadows(diffs, dists, obstacles - origin_pos)
        self.board = self.board.reshape(WINDOW_WIDTH*WINDOW_HEIGHT, 3)
        self.board += np.asarray([dists, dists, dists]).transpose() * np.asarray(color) * max_intensity
        self.board = np.reshape(self.board, (WINDOW_WIDTH, WINDOW_HEIGHT, 3))
        self.board = np.clip(self.board, 0, 255)

    def commit_renders(self):
        surf = pygame.surfarray.make_surface(self.board)
        surf = pygame.transform.scale(surf, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.screen_commit.blit(surf, (0, 0))

    def clear_board(self):
        self.board = np.zeros((WINDOW_WIDTH, WINDOW_HEIGHT, 3))

class Game():
    def __init__(self):
        pygame.init()
        pygame.display.init()

        self.clock = pygame.time.Clock()

        self.disp = Display()

        self.players = []

    def run(self):
        self.disp.clear_screen()

        player_1_control = [pygame.K_UP,
                            pygame.K_LEFT,
                            pygame.K_DOWN,
                            pygame.K_RIGHT]
        player_1_color = PLAYER_COLORS[0]
        player_1 = Player(1, player_1_color, player_1_control, [30, 30])

        player_2_control = [pygame.K_w,
                            pygame.K_a,
                            pygame.K_s,
                            pygame.K_d]
        player_2_color = PLAYER_COLORS[1]
        player_2 = Player(2, player_2_color, player_2_control, [WINDOW_WIDTH - 30, 30])

        player_3_control = [pygame.K_i,
                            pygame.K_j,
                            pygame.K_k,
                            pygame.K_l]
        player_3_color = PLAYER_COLORS[2]
        player_3 = Player(3, player_3_color, player_3_control, [30, WINDOW_HEIGHT - 30])

        player_4_control = [pygame.K_t,
                            pygame.K_f,
                            pygame.K_g,
                            pygame.K_h]
        player_4_color = PLAYER_COLORS[3]
        player_4 = Player(4, player_4_color, player_4_control, [WINDOW_WIDTH - 30, WINDOW_HEIGHT - 30])

        self.players = [player_1,
            player_2]

        self.obstacle_list = np.asarray(OBSTACLE_SET_1)

        self.pos_list = []
        for x in range(WINDOW_WIDTH):
            for y in range(WINDOW_HEIGHT):
                self.pos_list.append([x, y])
        self.pos_list = np.asarray(self.pos_list)

        while True:
            self.disp.clear_screen()
            for player in self.players:
                player.check_movement()
                player.check_brightness()
                a = self.disp.render_light(player.color,
                                        player.pos,
                                        self.pos_list,
                                        self.obstacle_list,
                                        max_intensity = player.brightness)
            self.disp.commit_renders()
            pygame.display.flip()

            print(self.clock.tick())

if __name__ == '__main__':
    game = Game()
    game.run()
