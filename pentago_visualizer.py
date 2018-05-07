import pygame, sys
from pygame.locals import *
import pentago
import random
import copy
pygame.font.init()
import numpy as np

##COLORS##
#             R    G    B 
WHITE    = (255, 255, 255)
BLACK    = (0,   0,   0)
BROWN   = (130, 82,   0)


class Game:
    def __init__(self):
        self.graphics = Graphics()
        self.board = Board()
        self.game_state, self.open_positions, _ = pentago.init_game()
        self.player_color = BLACK
        
    def setup(self):
        self.graphics.setup_window()

    def event_loop(self):
        self.mouse_pos = self.graphics.board_coords(pygame.mouse.get_pos()) # what square is the mouse in?
        self.x,  self.y, self.x_end, self.y_end = 0, 0, 0, 0
        self.dragging = False
        self.quad = 1
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                self.terminate_game()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                (self.x,self.y) = self.mouse_pos
                fake_game_state = np.copy(self.game_state)
                fake_game_state[0][self.y][self.x] = 1
                self.board.update_board(fake_game_state)
            if event.type == pygame.KEYDOWN:
                if event.key == K_1:
                    self.quad = 1
                if event.key == K_2:
                    self.quad = 2
                if event.key == K_3:
                    self.quad = 3
                if event.key == K_4:
                    self.quad = 4
                if event.key == K_COMMA:
                    self.game_state, self.open_positions, _ = pentago.move(self.game_state, [self.x,self.y], self.quad, False)
                    self.board.update_board(self.game_state)
                    self.update()
                    pygame.time.wait(2000)
                    self.game_state, self.open_positions, _ = pentago.move_debug(self.game_state, random.choice(self.open_positions), random.randint(1, 4), random.randint(0, 1))
                    self.board.update_board(self.game_state)
                if event.key == K_PERIOD:
                    self.game_state, self.open_positions, _ = pentago.move(self.game_state, [self.x,self.y], self.quad, True)
                    self.board.update_board(self.game_state)
                    self.update()
                    pygame.time.wait(2000)
                    self.game_state, self.open_positions, _ = pentago.move_debug(self.game_state, random.choice(self.open_positions), random.randint(1, 4), random.randint(0, 1))
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
                    pygame.draw.circle(self.screen, WHITE, self.pixel_coords((x,y)), self.piece_size)
                elif board.matrix[x][y].occupant == "BLACK":
                    pygame.draw.circle(self.screen, BLACK, self.pixel_coords((x,y)), self.piece_size)

    def pixel_coords(self, board_coords):
 
        return (board_coords[0] * self.square_size + self.piece_size, board_coords[1] * self.square_size + self.piece_size)
    
    def board_coords(self, coords):
        
        (pixel_x, pixel_y) = coords

        return (int(pixel_x / self.square_size), int(pixel_y / self.square_size))	

    def draw_message(self, message):
 
        self.message = True
        self.font_obj = pygame.font.Font('freesansbold.ttf', 44)
        self.text_surface_obj = self.font_obj.render(message, True, WHITE, BLACK)
        self.text_rect_obj = self.text_surface_obj.get_rect()
        self.text_rect_obj.center = (self.window_size / 2, self.window_size / 2)

class Board:
    def __init__(self):
        self.matrix =  [[""] * 6 for i in range(0,6)]

        for x in range(0,6):
            for y in range(0,6):
                self.matrix[y][x] = Space(WHITE)
    
    #takes in numpy array of gamestate (no moves or winner)
    def update_board(self, board_mat):

        for y in reversed(range(0,6)):
            for x in range(0,6):
                if board_mat[0, x, y] == 1:
                    self.matrix[y][x].occupant = "BLACK"
                elif board_mat[1, x, y] == 1:
                    self.matrix[y][x].occupant = "WHITE"
                else:
                    self.matrix[y][x].occupant = ""     
    

class Space:
	def __init__(self, color, occupant = None):
		self.color = color 
		self.occupant = occupant # occupant is a Square object

def main():
	game = Game()
	game.main()

if __name__ == "__main__":
	main()