# -*- coding: utf-8 -*-
"""
Created on Wed May  2 21:34:32 2018

@author: Miranda
"""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset
from torch.autograd import Variable
import torch.nn.functional as F
import torch.optim as optim
import pentago
import penntago_game_tree

#define possible rotations
rotations = [[1, False], [2,False], [3,False], [4,False], [1, True], [2,True], [3,True], [4,True]]
    
def get_possible_moves(gamestate):
    #print(gamestate)
    viable_positions = gamestate[1]
    move_options = [[pos,rot] for pos in viable_positions for rot in rotations]
    return move_options

def tree_update(node):
    parent_node = node.parent
    while parent_node is not None:
        parent_node.update(node.W, node.p)
        parent_node = parent_node.parent

def select_move(gamestate, v_learner, p_learner):
 #create new tree
    move_tree = penntago_game_tree.Tree(gamestate)
    current_node = move_tree.root

#do this 1600 times:
    for i in range(0, 1600):
        #get child nodes
        children = current_node.get_children()
        gamestate = current_node.gamestate
    #if there are children:
        if (len(children) != 0):
            #get Q of leaves (win chance)
            #get U of leaves (exploration factor)
            #find highest Q+U as new node
            best_choice = children[0]
            for j in range(0, len(children)):
                current_confidence = children[j].Q+children[j].U
                best_confidence = best_choice.Q+best_choice.U
                if (current_confidence > best_confidence):
                    best_choice = children[j]
            current_node = best_choice
        #if there are no children:
        else:
            if (current_node.complete_game == 0):
                #this should actually be the gamestate associated with the node, not with the turn
                player_moves = get_possible_moves(gamestate)
                #print(player_moves)
                #show_board(gamestate[0])
                for p_move in player_moves:
                    #print(gamestate[0], p_move[0], p_move[1][0], p_move[1][1])
                    new_gamestate = pentago.move(gamestate[0], p_move[0], p_move[1][0], p_move[1][1])
                    winner = new_gamestate[2]
                    board = new_gamestate[0]
                    #predict v and p for this node using learner
                    #print(torch.from_numpy(np.array(new_gamestate)).float().unsqueeze(0))
                    #print(Variable(torch.from_numpy(np.array(new_gamestate)).float().unsqueeze(0)))
                    v_prediction = v_learner(Variable(torch.from_numpy(np.array(board)).float().unsqueeze(0)).view(1,1,108))
                    v = v_prediction.data.numpy()[0]
                    p_prediction = p_learner(Variable(torch.from_numpy(np.array(board)).float().unsqueeze(0)).view(1,1,108))
                    p = p_prediction.data.numpy()[0]
                    #add a leaf for each possible move
                    leaf = penntago_game_tree.Node(new_gamestate)
                    leaf.set_parent(current_node)
                    #print([p_move[0][0], p_move[0][1], p_move[1][0], p_move[1][1]])
                    leaf.define_previous_move([p_move[0], p_move[1][0], p_move[1][1]])
                    current_node.add_child(leaf)
                    leaf.update(v, p)
                    #update all parent nodes
                    tree_update(leaf)
                    if (winner != -1):
                        leaf.complete_game = 1
            else:
                current_node.N += 1
            #go back to the top and do it again                                                                                                   
            current_node = move_tree.root
    
    #pick the most traveled route
    move_nodes = move_tree.root.get_children()
    selected_move = move_nodes[0]
    for i in range(0, len(move_nodes)):
        current_N = move_nodes[i].N
        best_N = selected_move.N
        if (current_N > best_N):
            selected_move = move_nodes[i]
    #output move and N
    return([best_N, selected_move.prev_move])
    
        
def play_game(v_learner, p_learner):
    #new game
    gamestate = pentago.init_game()
    
    #some useful lists to return later
    black_player_moves = []
    white_player_moves = []
    
    #while there is no winner
    game_winner = -1
    while (game_winner == -1):   
        #show_board(gamestate[0])
        N, next_move = select_move(gamestate, v_learner, p_learner)
        #store gamestate (before move) and N, also a dummy variable to become winner (0) FOR EACH PLAYER
        if (gamestate[0][2][0][0] == 0):
            black_player_moves.append([gamestate[0], N, 0])
        else:
            white_player_moves.append([gamestate[0], N, 0])
        gamestate = pentago.move(gamestate[0], next_move[0], next_move[1], next_move[2])
        #print(N)
        game_winner = gamestate[2]
    #if winner is found, update all previous entries to reflect (-1 for loss, 1 for win)
        #print(game_winner)
    print(game_winner)
    if (game_winner == 0):
        print("black won!")
        pentago.show_board(gamestate[0])
        for i in range(0,len(black_player_moves)):
            black_player_moves[i][2] = 1
        for i in range(0, len(white_player_moves)):
            white_player_moves[i][2] = -1
    elif(game_winner == 1):
        print("white won!")
        pentago.show_board(gamestate[0])
        for i in range(0,len(black_player_moves)):
            black_player_moves[i][2] = -1
        for i in range(0, len(white_player_moves)):
            white_player_moves[i][2] = 1        
    #return the datapoints from this game
#    print(black_player_moves)
    black_player_moves.extend(white_player_moves)
    return(black_player_moves)

class Dataset(Dataset):

    def __init__(self, X, Y):
        
        X = np.array(X)
        Y = np.array(Y)  
        
        self.len = X.shape[0]
        self.x_data = torch.from_numpy(X).float()
        self.y_data = torch.from_numpy(Y).float()

    def __len__(self):
        
        return self.len

    def __getitem__(self, idx):
        
        return self.x_data[idx], self.y_data[idx]    

class Pentago_Net(nn.Module):
    def __init__(self):
        super(Pentago_Net, self).__init__()
        self.fc1 = nn.Linear(108, 36)
        self.fc2 = nn.Linear(36, 1)

    def forward(self, x):
        out = F.relu(self.fc1(x))
        out = out.view(out.size(0), -1)
        out = F.relu(self.fc2(out))        
        return out

#create learners
v_net = Pentago_Net()
p_net = Pentago_Net()

# Specify the loss function
criterion = nn.CrossEntropyLoss()

# Specify the optimizer
v_optimizer = optim.SGD(v_net.parameters(), lr=0.001, momentum=0.9, weight_decay=5e-4)
p_optimizer = optim.SGD(p_net.parameters(), lr=0.001, momentum=0.9, weight_decay=5e-4)

#play game against self
data_and_labels = play_game(v_net, p_net)

v_pred = v_net(Variable(torch.from_numpy(np.array(np.array(data_and_labels)[:,0].tolist())).float().unsqueeze(0)).view(len(data_and_labels),1,108))
p_pred = p_net(Variable(torch.from_numpy(np.array(np.array(data_and_labels)[:,0].tolist())).float().unsqueeze(0)).view(len(data_and_labels),1,108))

v_true = Variable(torch.from_numpy(np.array(np.array(data_and_labels)[:,1].tolist())).float())
p_true = Variable(torch.from_numpy(np.array(np.array(data_and_labels)[:,1].tolist())).float())

# Calculate the loss using predicted labels and ground truth labels
v_loss = criterion(v_pred, v_true.long())
p_loss = criterion(v_pred, p_true.long())       
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




























