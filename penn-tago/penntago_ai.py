import random
import functools
import penntago_montecarlo


class Player:
    def __init__(self, type_string, ml_1=None, ml_2=None):
        if type_string == "random":
            self.select_move = select_random_move
        elif type_string == "montecarlo_quick":
            self.select_move = functools.partial(penntago_montecarlo.select_move, ml_1, ml_2, 0.0001)
        elif type_string == "montecarlo_normal":
            self.select_move = functools.partial(penntago_montecarlo.select_move, ml_1, ml_2, 0.5)
        elif type_string == "montecarlo_slow":
            self.select_move = functools.partial(penntago_montecarlo.select_move, ml_1, ml_2, 5)
        else:
            raise ValueError("Invalid player type. See penntago_ai.py for options.")


def select_random_move(_1, valid_moves, _2):
    return random.choice(valid_moves), None
