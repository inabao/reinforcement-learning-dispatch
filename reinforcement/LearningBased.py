import os
import pickle
import time

import numpy as np
import torch
from torch import nn
from setting import *
from reinforcement.model import BasicNetwork

modelPath = "model/%d_%s.pth" % (fragment, modelType)
time_slots = 86400 // fragment
model = BasicNetwork(time_slots)
lossFunction = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
amountClips = (6, 28)

def stateValueInit():
    if not os.path.exists("model"):
        os.makedirs("model")
    global stateValue
    global model
    if os.path.exists(modelPath):
        model.load_state_dict(torch.load(modelPath))
        model.eval()
    global lossFunction, optimizer
    lossFunction = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)


def stateValueSave():
    torch.save(model.state_dict(), modelPath)


def assess(solution, index):
    time_batch_before = torch.zeros((len(solution), time_slots))
    time_batch_before[:, index] = 1
    loc_batch_before = []
    if len(solution) == 0: return 0
    orders, _ = zip(*solution)
    for order in orders:
        startx = ((order.pickX - XREGION[0]) / (XREGION[1] - XREGION[0])) - 0.5
        starty = ((order.pickY - YREGION[0]) / (YREGION[1] - YREGION[0])) - 0.5
        loc_batch_before.append([startx, starty])
    loc_batch_before = torch.tensor(loc_batch_before)
    goal, _ = target(orders, index)
    goal = torch.from_numpy(goal.reshape((len(goal), 1))).to(torch.float32)
    goal = (torch.clip(goal, min=amountClips[0], max=amountClips[1]) - amountClips[0]) / (amountClips[1] - amountClips[0])
    y_hat = model(time_batch_before, loc_batch_before)
    global lossFunction
    loss = lossFunction(y_hat, goal)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()


def target(orders, index):
    rewards = []
    rounds = []
    time_batch_before = torch.zeros((len(orders), time_slots), dtype=torch.float32)
    time_batch_before[:, index] = 1
    loc_batch_before = []
    loc_batch_after = []
    time_batch_after = np.zeros((len(orders), time_slots), dtype=np.float32)
    for i, order in enumerate(orders):
        endIndex = int(index + (order.dropoffTime - order.pickTime) // fragment)
        reward = order.totalAmount
        round = (endIndex - index)
        if round == 0: round += 1
        fragmentReward = reward / round
        discountReward = fragmentReward * (1 - discount ** round) / (1 - discount)
        rewards.append(discountReward)
        rounds.append(round)
        startx = ((order.pickX - XREGION[0]) / (XREGION[1] - XREGION[0])) - 0.5
        starty = ((order.pickY - YREGION[0]) / (YREGION[1] - YREGION[0])) - 0.5
        loc_batch_before.append([startx, starty])
        endx = ((order.dropX - XREGION[0]) / (XREGION[1] - XREGION[0])) - 0.5
        endy = ((order.dropY - YREGION[0]) / (YREGION[1] - YREGION[0])) - 0.5
        loc_batch_after.append([endx, endy])
        if endIndex < 1440:
            time_batch_after[i][endIndex] = 1
        else:
            time_batch_after[i][0] = 1
    rewards = np.array(rewards)
    rounds = np.array(rounds)
    loc_batch_before = torch.tensor(loc_batch_before, dtype=torch.float32)
    loc_batch_after = torch.tensor(loc_batch_after, dtype=torch.float32)
    time_batch_after = torch.from_numpy(time_batch_after)
    global model
    rewards_after = model(time_batch_before, loc_batch_before)
    rewards_after = rewards_after.detach().numpy().flatten() * amountClips[1]
    mask = time_batch_after[:, 0] == 1
    mask = mask.flatten()
    try:
        rewards_after[mask] = 0
    except:
        pass
    rewards_before = model(time_batch_after, loc_batch_after).detach().numpy().flatten() * amountClips[1]
    return rewards + rewards_after * (discount ** rounds), rewards_before


def reward2discount(orders, index):
    goal, current = target(orders, index)
    return goal - current

