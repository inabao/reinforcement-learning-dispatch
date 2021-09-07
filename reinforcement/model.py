import torch
from torch import nn

class BasicNetwork(nn.Module):
    def __init__(self, time_slots):
        super(BasicNetwork, self).__init__()
        self.flatten = nn.Flatten()
        self.activation = nn.Tanh()
        self.locEmbedding = nn.Linear(2, 64, dtype=torch.float32)
        self.timeEmbedding = nn.Linear(time_slots, 64, dtype=torch.float32)
        self.conv1d = nn.Conv1d(2, 2, kernel_size=(3,), padding="same")
        self.norm = nn.BatchNorm1d(2)
        self.con = nn.Linear(128, 1, dtype=torch.float32)
        self.sigmoid = nn.Sigmoid()
    def forward(self, time, loc):
        t = self.activation(self.timeEmbedding(time))
        c = self.activation(self.locEmbedding(loc))
        x = torch.stack((t, c), dim=1)
        x = self.conv1d(x)
        x = self.norm(x)
        x = self.flatten(x)
        x = self.con(x)
        x = self.sigmoid(x)
        return x

if __name__ == '__main__':
    time_slots = 1440
    time = torch.zeros((2, time_slots))
    time[0][1] += 1
    time[1][79] += 1
    time = time.cuda()
    loc = torch.tensor([[-0.36821, -0.68771], [-0.43, -0.29]])
    loc = loc.cuda()
    model = BasicNetwork(time_slots).to("cuda:0")
    print(model(time, loc))