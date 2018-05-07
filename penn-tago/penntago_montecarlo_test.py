import numpy as np

import torch

import penntago_nn
import penntago_game
import penntago_ai

"""
penntago_montecarlo_train.py, saves and reloads training Monte Carlo tree.
"""

MONTECARLO_SPEED = "quick"

FOLDER_PATH = "./ai_states/montecarlo/" + MONTECARLO_SPEED + "/"

EPOCH_SIZE = 100

v_net = penntago_nn.NeuralNet()
p_net = penntago_nn.NeuralNet()

# print("Columns: Black Win, White Win, Tie")
# for epoch in [10, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]:
#     v_net.load_state_dict(torch.load(FOLDER_PATH + str(epoch) + "v"))
#     p_net.load_state_dict(torch.load(FOLDER_PATH + str(epoch) + "p"))
#
#     results = np.zeros(EPOCH_SIZE)
#     for i in range(0, EPOCH_SIZE):
#         # Play a game against self
#         game = penntago_game.Game(penntago_ai.Player("montecarlo_" + MONTECARLO_SPEED, v_net, p_net),
#                                   penntago_ai.Player("random"))
#
#         while game.status_code == -1:
#             game.take_turn()
#         results[i] = game.status_code
#
#     black_wins = np.sum(results == 0)
#     white_wins = np.sum(results == 1)
#     ties = np.sum(results == 2)
#
#     print(str(black_wins) + ", " + str(white_wins) + ", " + str(ties))

print("Columns: Black Win, White Win, Tie")
v500_net = penntago_nn.NeuralNet()
p500_net = penntago_nn.NeuralNet()
v500_net.load_state_dict(torch.load(FOLDER_PATH + str(500) + "v"))
p500_net.load_state_dict(torch.load(FOLDER_PATH + str(500) + "p"))
for epoch in [10, 100, 200, 300, 400, 600, 700, 800, 900, 1000]:
    v_net.load_state_dict(torch.load(FOLDER_PATH + str(epoch) + "v"))
    p_net.load_state_dict(torch.load(FOLDER_PATH + str(epoch) + "p"))

    results = np.zeros(10)
    for i in range(0, 10):
        # Play a game against self
        game = penntago_game.Game(penntago_ai.Player("montecarlo_" + MONTECARLO_SPEED, v_net, p_net),
                                  penntago_ai.Player("montecarlo_" + MONTECARLO_SPEED, v500_net, p500_net))

        while game.status_code == -1:
            game.take_turn()
        results[i] = game.status_code

    black_wins = np.sum(results == 0)
    white_wins = np.sum(results == 1)
    ties = np.sum(results == 2)

    print(str(black_wins) + ", " + str(white_wins) + ", " + str(ties))
