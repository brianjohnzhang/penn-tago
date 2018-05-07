import math


class Node:
    def __init__(self, game_state, valid_moves, status_code):
       
        self.game_state = game_state
        self.valid_moves = valid_moves
        self.status_code = status_code
        
        # number of times this node has been selected
        self.N = 1
        
        # number of leaves reachable from this node which correspond to winning games
        self.W = 0
        
        # probability of making this move FROM ANY STATE
        self.p = 0
        
        # win rate
        self.Q = 0
        
        # exploration factor
        self.U = 0
        
        # has an empty list of children
        self.children = []
        
        # has a parent, yet to be assigned
        self.parent = None
        
        # has a previous move, potentially
        self.prev_move = []
    
    def get_children(self):
        return self.children
        
    def update(self, v, p):
        self.p = p
        self.N += 1
        self.W += v
        self.Q = self.W/self.N
        self.U = 0.1*self.p*math.sqrt(self.N)/(1+self.N)
        
    def set_parent(self, parent_node):
        self.parent = parent_node
        
    def add_child(self, child_node):
        self.children.append(child_node)
    
    def define_previous_move(self, move):
        self.prev_move = move


class Tree:
    def __init__(self, game_state, valid_moves, status_code):
        self.root = Node(game_state, valid_moves, status_code)
        self.nodes = [self.root]
    
    def add(self, node):
        self.nodes.append(node)
