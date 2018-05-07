import os
import random
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable

import pentago
import penntago_tree
import penntago_nn
import penntago_montecarlo

"""
penntago_montecarlo.py, combines and executes Pentago games with the tree and neural network.
"""

v_net = penntago_nn.NeuralNet()
p_net = penntago_nn.NeuralNet()

most_recent = 0
for (_, _, filenames) in os.walk("./ai_states/montecarlo"):
    for filename in filenames:
        if filename != "" and int(filename[0:len(filename)-1]) > most_recent:
            most_recent = int(filename[0:len(filename)-1])
if most_recent != 0:
    v_net.load_state_dict(torch.load("./ai_states/montecarlo/" + str(most_recent) + "v"))
    p_net.load_state_dict(torch.load("./ai_states/montecarlo/" + str(most_recent) + "p"))

results = np.zeros(100)
for i in range(0, 100):
    game_state, open_positions, game_status = pentago.init_game()
    while game_status == -1:
        _, next_move = penntago_montecarlo.select_move(game_state, open_positions, game_status, v_net, p_net)
        game_state, open_positions, game_status = pentago.move_debug(game_state, next_move[0], next_move[1], next_move[2])
        if game_status != -1:
            break
        game_state, open_positions, game_status = pentago.move_debug(game_state, random.choice(open_positions),
                                                                     random.randint(1, 4), random.randint(0, 1))
    results[i] = game_status

black_wins = np.sum(results == 0)
white_wins = np.sum(results == 1)
ties = np.sum(results == 2)

print(str(black_wins) + ", " + str(white_wins) + ", " + str(ties))