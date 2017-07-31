from torch.nn import Module
import torch.nn as nn
from torch.nn import functional as F
from torch.nn import init
import torch
import torch.optim as optim

class PolicyNet(Module):
    def __init__(self):
        self.optimizer = None
        # the inputs should be [80, 80, 3]
        super(PolicyNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 5, kernel_size=3, padding=1)  # [80, 80, 5]
        self.conv2 = nn.Conv2d(5, 10, kernel_size=3, padding=1)  # [80, 80, 10]
        self.fc1 = nn.Linear(64000, 20)  # [40]
        self.fc2 = nn.Linear(20, 1)  # [1]
        self.reset_parameters()

    def forward(self, inputs):
        net = self.conv1(inputs)
        net = F.relu(net, inplace=True)
        net = self.conv2(net)
        net = F.relu(net, inplace=True)
        net = net.view(-1, 80 * 80 * 10)
        net = self.fc1(net)
        net = F.relu(net, inplace=True)
        net = self.fc2(net)
        net = F.sigmoid(net)
        return net

    def reset_parameters(self):
        for para in self.children():
            if isinstance(para, nn.AvgPool2d): continue
            init.xavier_normal(para.weight)
            init.constant(para.bias, val=0)

    def weight_decay_loss(self, weight_decay=0.0005):
        loss = 0.
        for child in self.children():
            loss += torch.norm(child.weight, p=2) ** 2
        return weight_decay * loss

    def get_optimizer(self):
        if self.optimizer is None:
            self.optimizer = optim.RMSprop(self.parameters(), lr=1e-5)
        return self.optimizer

if __name__ == '__main__':
    net = PolicyNet()
