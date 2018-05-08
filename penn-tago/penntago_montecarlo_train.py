import os
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable

import penntago_nn
import penntago_game
import penntago_ai

import matplotlib.pyplot as plt

"""
penntago_montecarlo_train.py, saves and reloads training Monte Carlo tree.
"""

MONTECARLO_SPEED = "slow"

FOLDER_PATH = "./ai_states/montecarlo/" + MONTECARLO_SPEED + "/"
NUM_CYCLES = 10
GAMES_PER_CYLCE = 10
EPOCH_SIZE = 50

v_net = penntago_nn.NeuralNet()
p_net = penntago_nn.NeuralNet()

most_recent = 0
for (_, _, filenames) in os.walk(FOLDER_PATH):
    for filename in filenames:
        if filename != "" and int(filename[0:len(filename)-1]) > most_recent:
            most_recent = int(filename[0:len(filename)-1])
if most_recent != 0:
    v_net.load_state_dict(torch.load(FOLDER_PATH + str(most_recent) + "v"))
    p_net.load_state_dict(torch.load(FOLDER_PATH + str(most_recent) + "p"))

for n in range(0, NUM_CYCLES):
    print(n)
    game_history_states = []
    game_history_travel = []
    game_history_wins = []
    v_loss_np = np.zeros((EPOCH_SIZE))
    p_loss_np = np.zeros((EPOCH_SIZE))
    for i in range(0, GAMES_PER_CYLCE):

        # Specify the loss function
        criterion = nn.CrossEntropyLoss()

        # Specify the optimizer
        v_optimizer = optim.SGD(v_net.parameters(), lr=0.001, momentum=0.9, weight_decay=5e-4)
        p_optimizer = optim.SGD(p_net.parameters(), lr=0.001, momentum=0.9, weight_decay=5e-4)

        # Play a game against self
        game = penntago_game.Game(penntago_ai.Player("montecarlo_" + MONTECARLO_SPEED, v_net, p_net),
                                  penntago_ai.Player("montecarlo_" + MONTECARLO_SPEED, v_net, p_net))
        while game.status_code == -1:
            game.take_turn()

        # Store game state history,  N (other_history), and a stand-in for the winner label
        state_history = game.get_state_history()
        travel_history = game.get_other_history()
        win_history = []

        # if winner is found, update all previous entries to reflect (0 for loss, 0.5 for tie, 0.9999 for win)
        if game.status_code == 0:
            for k in range(0, len(state_history)):
                if k % 2 == 0:
                    win_history.append(.9999)
                else:
                    win_history.append(0)
        elif game.status_code == 1:
            for k in range(0, len(state_history)):
                if k % 2 == 1:
                    win_history.append(.9999)
                else:
                    win_history.append(0)
        else:
            for k in range(0, len(state_history)):
                win_history.append(0.5)
        
        game_history_states.append(state_history)
        game_history_travel.append(travel_history)
        game_history_wins.append(win_history)
        
    for epoch in range(0, EPOCH_SIZE):
        #trim data through ranndom sampling
        data_picked = np.random.randint(0,len(game_history_states),100)
        
        batch_states = [game_history_states[i] for i in data_picked]
        batch_travel = [game_history_travel[i] for i in data_picked]
        batch_wins = [game_history_wins[i] for i in data_picked]
        
        data = Variable(torch.from_numpy(np.array(batch_states)).float())
        v_pred = v_net(data.view(len(batch_states), 1, 108))
        p_pred = p_net(data.view(len(batch_states), 1, 108))
    
        v_true = Variable(torch.from_numpy(np.array(batch_wins)).float())
        p_true = Variable(torch.from_numpy(np.array(batch_travel)).float())
    
         # Calculate the loss using predicted labels and ground truth labels
        v_loss = criterion(v_pred, v_true.long())
        p_loss = criterion(p_pred, p_true.long())
    
        # zero gradient
        v_optimizer.zero_grad()
        p_optimizer.zero_grad()
        # Backpropogates to compute gradient
        v_loss.backward()
        p_loss.backward()
        # Updates the weghts
        v_optimizer.step()
        p_optimizer.step()
        
        v_batch_loss = sum(v_loss.data.numpy())
        p_batch_loss = sum(p_loss.data.numpy())
        
        v_loss_np[epoch] = v_batch_loss/EPOCH_SIZE
        p_loss_np[epoch] = p_batch_loss/EPOCH_SIZE
        
    # Plot the loss over epoch
    plt.figure()
    plt.plot(epoch, v_loss_np)
    plt.title('loss over epochs, v')
    plt.xlabel('Number of Epoch')
    plt.ylabel('Loss')
    
    # Plot the loss over epoch
    plt.figure()
    plt.plot(epoch, v_loss_np)
    plt.title('loss over epochs, v')
    plt.xlabel('Number of Epoch')
    plt.ylabel('Loss')
        

    torch.save(v_net.state_dict(), FOLDER_PATH + str(int((n+1) * EPOCH_SIZE)) + "v")
    torch.save(p_net.state_dict(), FOLDER_PATH + str(int((n+1) * EPOCH_SIZE)) + "p")
