import os
import time
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable

import pentago
import penntago_tree
import penntago_nn


"""
penntago_montecarlo.py, combines and executes Pentago games with the tree and neural network.
"""


# Define possible rotations
ALL_ROTATIONS = [(1, False), (2, False), (3, False), (4, False), (1, True), (2, True), (3, True), (4, True)]
TURN_TIME_LIMIT = .01


# Does something to the tree
def update_tree(node):
    parent_node = node.parent
    while parent_node is not None:
        parent_node.update(node.W, node.p)
        parent_node = parent_node.parent


# Collects a list of postions, rotations, and rotation directions as sublists
def get_possible_moves(open_positions):
    return [[pos, rot[0], rot[1]] for pos in open_positions for rot in ALL_ROTATIONS]


# Selects a move based on the valid trees
def select_move(game_state, open_positions, game_status, v_learner, p_learner):
    # Create new tree based on current game state
    current_tree = penntago_tree.Tree(game_state, open_positions, game_status)
    current_node = current_tree.root

    # Do this 1600 times, or 10 seconds at most:
    t = time.time()
    for _ in range(0, 1600):
        # Get child nodes
        children = current_node.get_children()

        # If there are children:
        if len(children) != 0:
            # get Q of leaves (win chance)
            # get U of leaves (exploration factor)
            # find highest Q+U as new node
            best_choice = children[0]
            for j in range(0, len(children)):
                current_confidence = children[j].Q + children[j].U
                best_confidence = best_choice.Q + best_choice.U
                if any(current_confidence > best_confidence):
                    best_choice = children[j]

            current_node = best_choice
            current_node.N += 1

        # If there are no children:
        else:
            if current_node.game_status == -1:
                # this should actually be the gamestate associated with the node, not with the turn
                for possible_move in get_possible_moves(current_node.open_positions):
                    game_state_new, open_positions_new, game_status_new = pentago.move(current_node.game_state,
                                                                                       possible_move[0],
                                                                                       possible_move[1],
                                                                                       possible_move[2])

                    # predict v and p for this node using learner
                    # print(torch.from_numpy(np.array(new_gamestate)).float().unsqueeze(0))
                    # print(Variable(torch.from_numpy(np.array(new_gamestate)).float().unsqueeze(0)))
                    v_prediction = v_learner(Variable(torch.from_numpy(game_state_new).float().unsqueeze(0))
                                             .view(1, 1, 108))
                    v = v_prediction.data.numpy()[0]
                    p_prediction = p_learner(Variable(torch.from_numpy(game_state_new).float().unsqueeze(0))
                                             .view(1, 1, 108))
                    p = p_prediction.data.numpy()[0]

                    # Add a leaf for each possible move
                    leaf = penntago_tree.Node(game_state_new, open_positions_new, game_status_new)
                    leaf.set_parent(current_node)
                    # print([p_move[0][0], p_move[0][1], p_move[1][0], p_move[1][1]])
                    leaf.define_previous_move([possible_move[0], possible_move[1], possible_move[2]])
                    current_node.add_child(leaf)
                    leaf.update(v, p)

                    # Update all parent nodes
                    update_tree(leaf)
            else:
                current_node.N += 1

            # go back to the top and do it again
            current_node = current_tree.root
        if time.time() - t > TURN_TIME_LIMIT:
            break
    
    # Pick the most traveled route
    possible_nodes = current_tree.root.get_children()
    selected_move = possible_nodes[0]
    N_total = 0

    for current_node in possible_nodes:
        N_total += current_node.N
        if current_node.N > selected_move.N:
            selected_move = current_node

    # output move and N
    return selected_move.N / N_total, selected_move.prev_move
    
        
def play_game(v_learner, p_learner):
    # New game
    game_state, open_positions, game_status = pentago.init_game()
    
    # History list
    moves_history = []

    t = time.time()
    while game_status == -1:
        N, next_move = select_move(game_state, open_positions, game_status, v_learner, p_learner)
        # Store game_state_old,  N, and a stand-in for the winner label
        moves_history.append([game_state, N, 0])

        game_state, open_positions, game_status = pentago.move(game_state, next_move[0], next_move[1], next_move[2])

        print("Moved, took " + str(time.time() - t) + " seconds.")
        t = time.time()

    # if winner is found, update all previous entries to reflect (-1 for loss, 1 for win)
    print(game_status)
    if game_status == 0:
        print("Black won!")
        pentago.show_board(game_state)
        for i in range(0, len(moves_history)):
            if i % 2 == 0:
                moves_history[i][2] = .9999
            else:
                moves_history[i][2] = 0
    elif game_status == 1:
        print("White won!")
        pentago.show_board(game_state)
        for i in range(0, len(moves_history)):
            if i % 2 == 0:
                moves_history[i][2] = 0
            else:
                moves_history[i][2] = .9999
    else:
        print("Tie game!")
        pentago.show_board(game_state)
        for i in range(0, len(moves_history)):
            moves_history[i][2] = 0.5
    # Return all datapoints from this game
    return moves_history


# Create learners
v_net = penntago_nn.NeuralNet()
p_net = penntago_nn.NeuralNet()

# Specify the loss function
criterion = nn.CrossEntropyLoss()

# Specify the optimizer
v_optimizer = optim.SGD(v_net.parameters(), lr=0.001, momentum=0.9, weight_decay=5e-4)
p_optimizer = optim.SGD(p_net.parameters(), lr=0.001, momentum=0.9, weight_decay=5e-4)

# Play a game against self
data_and_labels = play_game(v_net, p_net)

data = Variable(torch.from_numpy(np.array(np.array(data_and_labels)[:, 0].tolist())).float())
v_pred = v_net(data.view(len(data_and_labels), 1, 108))
p_pred = p_net(data.view(len(data_and_labels), 1, 108))

v_true = Variable(torch.from_numpy(np.array(np.array(data_and_labels)[:, 2].tolist())).float())
p_true = Variable(torch.from_numpy(np.array(np.array(data_and_labels)[:, 1].tolist())).float())

print(p_pred)
print(p_pred.shape)
print(v_true)
print(v_true.shape)
# Calculate the loss using predicted labels and ground truth labels
v_loss = criterion(v_pred, v_true.long())
p_loss = criterion(p_pred, p_true.long())
#print("epoch: ", epoch, "loss: ", loss.data[0])
        
# zero gradient
v_optimizer.zero_grad()
p_optimizer.zero_grad()        
# backpropogates to compute gradient
v_loss.backward()
p_loss.backward()
# updates the weghts
v_optimizer.step()
p_optimizer.step()
