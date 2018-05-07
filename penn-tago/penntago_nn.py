import numpy as np
import torch
import torch.nn
import torch.nn.functional
from torch.utils.data import Dataset


"""
penntago_nn.py, implements the neural network part of a Monte Carlo search tree
"""


class NeuralNet(torch.nn.Module):
    def __init__(self):
        super(NeuralNet, self).__init__()
        self.fc1 = torch.nn.Linear(3 * 6 * 6, 36)
        self.fc2 = torch.nn.Linear(36, 1)

    def forward(self, x):
        out = torch.nn.functional.relu(self.fc1(x))
        out = out.view(out.size(0), -1)
        out = torch.nn.functional.relu(self.fc2(out))
        return out
