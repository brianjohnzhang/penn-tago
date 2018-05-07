import numpy as np
import torch
import torch.nn
import torch.nn.functional
from torch.utils.data import Dataset


"""
penntago_nn.py, implements the neural network part of a Monte Carlo search tree
"""


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
