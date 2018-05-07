import pentago


class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.state_history = []
        self.move_history = []
        self.other_history = []
        self.game_state, self.valid_moves, self.status_code = pentago.init_game()

    def take_turn(self):
        if self.status_code == -1:
            if self.game_state[2, 0, 0] == 0:
                self.state_history.append(self.game_state)
                next_move, other = self.player1.select_move(self.game_state, self.valid_moves, self.status_code)
                self.move_history.append(next_move)
                if other is not None:
                    self.other_history.append(other)
                self.game_state, self.valid_moves, self.status_code = pentago.move(self.game_state, next_move)
            elif self.game_state[2, 0, 0] == 1:
                self.state_history.append(self.game_state)
                next_move, other = self.player2.select_move(self.game_state, self.valid_moves, self.status_code)
                self.move_history.append(next_move)
                if other is not None:
                    self.other_history.append(other)
                self.game_state, self.valid_moves, self.status_code = pentago.move(self.game_state, next_move)
        else:
            print("Game's already over.")

    def get_state_history(self):
        return self.state_history

    def get_move_history(self):
        return self.move_history

    def get_other_history(self):
        return self.other_history