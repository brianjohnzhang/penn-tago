import sys
import pygame

import pentago
import numpy as np
import torch

import penntago_nn, penntago_ai

# Colors
#         R    G    B
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
BROWN = (130, 82,   0)

pygame.font.init()

MONTECARLO_SPEED = "quick"
FOLDER_PATH = "./ai_states/montecarlo/" + MONTECARLO_SPEED + "/"
EPOCHS_TRAINED = 500


class Game:
    def __init__(self):
        v_net = penntago_nn.NeuralNet()
        p_net = penntago_nn.NeuralNet()
        v_net.load_state_dict(torch.load(FOLDER_PATH + str(EPOCHS_TRAINED) + "v"))
        p_net.load_state_dict(torch.load(FOLDER_PATH + str(EPOCHS_TRAINED) + "p"))
        self.ai = penntago_ai.Player("montecarlo_" + MONTECARLO_SPEED, v_net, p_net)
        self.graphics = Graphics()
        self.board = Board()
        self.game_state, self.valid_moves, self.status_code = pentago.init_game()
        self.player_color = BLACK
        self.mouse_pos = self.graphics.board_coords(pygame.mouse.get_pos())
        self.quad = 1
        self.dragging = False
        self.x, self.y, self.x_end, self.y_end = 0, 0, 0, 0

    def setup(self):
        self.graphics.setup_window()

    def event_loop(self):
        self.mouse_pos = self.graphics.board_coords(pygame.mouse.get_pos()) # what square is the mouse in?
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                self.terminate_game()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                (self.x, self.y) = self.mouse_pos
                print(self.mouse_pos)
                fake_game_state = np.copy(self.game_state)
                if fake_game_state[0][self.x][self.y] == 0 and fake_game_state[1][self.x][self.y] == 0:
                    fake_game_state[0][self.x][self.y] = 1
                    self.board.update_board(fake_game_state)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.quad = 1
                elif event.key == pygame.K_2:
                    self.quad = 2
                elif event.key == pygame.K_3:
                    self.quad = 3
                elif event.key == pygame.K_4:
                    self.quad = 4
                elif event.key == pygame.K_q:
                    print([[self.x, self.y], self.quad, True])
                    self.game_state, self.valid_moves, _ = pentago.move(self.game_state,
                                                                        [[self.x, self.y], self.quad, False])
                    self.board.update_board(self.game_state)
                    self.update()
                    pygame.time.wait(2000)
                    #
                    self.game_state, self.valid_moves, _ = pentago.move(self.game_state,
                                                                        self.ai.select_move(self.game_state,
                                                                                            self.valid_moves,
                                                                                            self.status_code)
                                                                        [0])
                    self.board.update_board(self.game_state)
                elif event.key == pygame.K_e:
                    print([[self.x, self.y], self.quad, True])
                    self.game_state, self.valid_moves, _ = pentago.move(self.game_state,
                                                                        [[self.x, self.y], self.quad, True])
                    self.board.update_board(self.game_state)
                    self.update()
                    pygame.time.wait(2000)
                    self.game_state, self.valid_moves, _ = pentago.move(self.game_state,
                                                                        self.ai.select_move(self.game_state,
                                                                                            self.valid_moves,
                                                                                            self.status_code)
                                                                        [0])
                    self.board.update_board(self.game_state)

    def update(self):
        self.graphics.update_display(self.board)

    def terminate_game(self):
        pygame.quit()
        sys.exit
        
    def main(self):
        self.setup()

        while True: # main game loop
            self.event_loop()
            self.update()           


class Graphics:
    def __init__(self):
        self.caption = "Pentago"

        self.fps = 60
        self.clock = pygame.time.Clock()

        self.window_size = 600
        self.screen = pygame.display.set_mode((self.window_size, self.window_size))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(BROWN)

        self.square_size = int(self.window_size / 6)
        self.piece_size = int(self.square_size / 2)

        self.message = False

    def setup_window(self):
        pygame.init()
        pygame.display.set_caption(self.caption)

    def update_display(self, board):
        self.screen.blit(self.background, (0,0))
        self.draw_board_pieces(board)
        self.draw_board_squares(board)

        if self.message:
            self.screen.blit(self.text_surface_obj, self.text_rect_obj)

        pygame.display.update()
        self.clock.tick(self.fps)

    def draw_board_squares(self, board):
        for x in range(0, 6):
            for y in range(0, 6):
                pygame.draw.rect(self.screen, board.matrix[x][y].color, (x * self.square_size, y * self.square_size, self.square_size, self.square_size), 1)
                if (x == 0 or x == 3) and (y == 0 or y == 3):
                    pygame.draw.rect(self.screen, board.matrix[x][y].color, (x * self.square_size, y * self.square_size, self.square_size*3, self.square_size*3), 4)

    def draw_board_pieces(self, board):
        
        for x in range(0, 6):
            for y in range(0, 6):
                if board.matrix[x][y].occupant == "WHITE":
                    pygame.draw.circle(self.screen, WHITE, self.pixel_coords((x, y)), self.piece_size)
                elif board.matrix[x][y].occupant == "BLACK":
                    pygame.draw.circle(self.screen, BLACK, self.pixel_coords((x, y)), self.piece_size)

    def pixel_coords(self, board_coords):
 
        return (board_coords[0] * self.square_size + self.piece_size, (5 - board_coords[1]) * self.square_size + self.piece_size)
    
    def board_coords(self, coords):
        (pixel_x, pixel_y) = coords
        return int(pixel_x / self.square_size), 5 - int(pixel_y / self.square_size)

    def draw_message(self, message):
        self.message = True
        self.font_obj = pygame.font.Font('freesansbold.ttf', 44)
        self.text_surface_obj = self.font_obj.render(message, True, WHITE, BLACK)
        self.text_rect_obj = self.text_surface_obj.get_rect()
        self.text_rect_obj.center = (self.window_size / 2, self.window_size / 2)


class Board:
    def __init__(self):
        self.matrix = [[""] * 6 for _ in range(0, 6)]

        for x in range(0, 6):
            for y in range(0, 6):
                self.matrix[x][y] = Space(WHITE)
    
    # takes in numpy array of gamestate (no moves or winner)
    def update_board(self, board_mat):

        for y in reversed(range(0, 6)):
            for x in range(0, 6):
                if board_mat[0, x, y] == 1:
                    self.matrix[x][y].occupant = "BLACK"
                elif board_mat[1, x, y] == 1:
                    self.matrix[x][y].occupant = "WHITE"
                else:
                    self.matrix[x][y].occupant = ""
    

class Space:
    def __init__(self, color, occupant=None):
        self.color = color
        self.occupant = occupant
    # occupant is a Square object


if __name__ == "__main__":
    game = Game()
    game.main()
