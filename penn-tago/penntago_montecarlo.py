import time

import torch
from torch.autograd import Variable

import pentago
import penntago_tree


"""
penntago_montecarlo.py, combines and executes Pentago games with the tree and neural network.
"""


# Recurses back up the tree, updating
def update_tree(node):
    parent_node = node.parent
    while parent_node is not None:
        parent_node.update(node.W, node.p)
        parent_node = parent_node.parent


# Selects a move based on the valid trees
def select_move(v_net, p_net, dt, game_state, valid_moves, status_code):
    # Create new tree based on current game state
    current_tree = penntago_tree.Tree(game_state, valid_moves, status_code)
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
                if current_confidence > best_confidence:
                    best_choice = children[j]

            current_node = best_choice
            current_node.N += 1

        # If there are no children:
        else:
            if current_node.status_code == -1:
                # this should actually be the gamestate associated with the node, not with the turn
                for move in current_node.valid_moves:
                    game_state_new, valid_moves_new, status_code_new = pentago.move(current_node.game_state, move)

                    # predict v and p for this node using learner
                    # print(torch.from_numpy(np.array(new_gamestate)).float().unsqueeze(0))
                    # print(Variable(torch.from_numpy(np.array(new_gamestate)).float().unsqueeze(0)))
                    v_prediction = v_net(Variable(torch.from_numpy(game_state_new).float().unsqueeze(0))
                                         .view(1, 1, 108))
                    v = v_prediction.data.numpy()[0]
                    p_prediction = p_net(Variable(torch.from_numpy(game_state_new).float().unsqueeze(0))
                                         .view(1, 1, 108))
                    p = p_prediction.data.numpy()[0]

                    # Add a leaf for each possible move
                    leaf = penntago_tree.Node(game_state_new, valid_moves_new, status_code_new)
                    leaf.set_parent(current_node)
                    # print([p_move[0][0], p_move[0][1], p_move[1][0], p_move[1][1]])
                    leaf.define_previous_move(move)
                    current_node.add_child(leaf)
                    leaf.update(v, p)

                    # Update all parent nodes
                    update_tree(leaf)
            else:
                current_node.N += 1

            # go back to the top and do it again
            current_node = current_tree.root
        if time.time() - t > dt:
            break

    # Pick the most traveled route, normalize the output
    possible_nodes = current_tree.root.get_children()
    selected_move = possible_nodes[0]
    total = 0

    for current_node in possible_nodes:
        total += current_node.N
        if current_node.N > selected_move.N:
            selected_move = current_node

    # output move and N
    return selected_move.prev_move, selected_move.N / total
