import os
import pickle
import numpy as np
from setting import *

stateValue = np.zeros((86400 // fragment, regionx, regiony))
statePath = "stateValue/%d_%d_%d.pl" % (regionx, regiony, fragment)


def regionDepart(loc, num_x=regionx, num_y=regiony, xregion=XREGION, yregion=YREGION):
    x, y = loc
    single_x = (xregion[1] - xregion[0]) / num_x
    single_y = (yregion[1] - yregion[0]) / num_y
    if xregion[0] < x < xregion[1] and yregion[0] < y < yregion[1]:
        return int((x - xregion[0]) / single_x), int((y - yregion[0]) / single_y)
    return -1, -1


def stateValueInit():
    if not os.path.exists("stateValue"):
        os.makedirs("stateValue")
    global stateValue
    if os.path.exists(statePath):
        with open(statePath, "rb") as f:
            stateValue = pickle.load(f)


def stateValueSave():
    with open(statePath, "wb") as f:
        pickle.dump(stateValue, f)


def assess(solution, index):
    if len(solution) == 0: return
    orders, _ = zip(*solution)
    loc = []
    for order, driver in solution:
        startx, starty = regionDepart((order.pickX, order.pickY))
        loc.append([startx, starty])
    x, y = zip(*loc)
    x, y = np.array(x), np.array(y)
    newReward = reward2discount(orders, index)
    stateValue[index][x, y] += learningRate * newReward




def reward2discount(orders, index):
    rewards = []
    for order in orders:
        endIndex = int(index + (order.dropoffTime - order.pickTime) // fragment)
        reward = order.totalAmount
        round = (endIndex - index)
        endx, endy = regionDepart((order.dropX, order.dropY))
        startx, starty = regionDepart((order.pickX, order.pickY))
        if round == 0: round += 1
        fragmentReward = reward / round
        discountReward = fragmentReward * (1 - discount ** round) / (1 - discount)
        global stateValue
        if endIndex >= 86400 // fragment:
            tmp = 0
        else:
            tmp = stateValue[endIndex][endx][endy]
        rewards.append(discountReward + discount ** round * tmp - stateValue[index][startx][starty])
    return np.array(rewards)


