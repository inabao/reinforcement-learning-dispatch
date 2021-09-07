import time

import numpy as np
from scipy.optimize import linear_sum_assignment
from setting import *
from reinforcement import reward2discount


np.random.seed(seed)


def match(orders: list, drivers: list, income=False, index=-1):
    ordersRewards = np.zeros((len(drivers), len(orders))) - 10
    if len(orders) == 0 or len(drivers) == 0: return ordersRewards
    driversLocation = np.array([[driver.x, driver.y] for driver in drivers])
    ordersLocation = np.array([[order.pickX, order.pickY] for order in orders]).T
    if index != -1:
        ordersReward = reward2discount(orders, index)
    elif income == False:
        ordersReward = np.ones(len(orders))
    else:
        ordersReward = np.array([order.totalAmount for order in orders])
    ordersSpeed = np.array([order.speed for order in orders])
    available = np.sum(np.abs(driversLocation[:,:,None] - ordersLocation[None,:,:]), axis=1)
    available = (available[:,] / ordersSpeed) > takeTime
    ordersRewards[:,] = ordersReward
    ordersRewards[available] = -10
    return ordersRewards




def reinforce(orders: list, drivers: list, index):
    available = -np.array(match(orders, drivers, index=index))
    row_ind, col_ind = linear_sum_assignment(available)
    res = []
    for i, j in zip(row_ind, col_ind):
        if available[i][j] != 0:
            res.append((orders[j], drivers[i]))
    return res




def bigrah_dispatch(orders: list, drivers: list, income: bool=False):
    available = -np.array(match(orders, drivers, income))
    row_ind, col_ind = linear_sum_assignment(available)
    res = []
    for i, j in zip(row_ind, col_ind):
        if available[i][j] != 0:
            res.append((orders[j], drivers[i]))
    return res

def random_dispatch(orders: list, drivers: list):
    np.random.shuffle(orders)
    np.random.shuffle(drivers)
    available = match(orders, drivers)
    res = []
    for i in range(len(drivers)):
        r = np.argwhere(available[i] == 1)
        if len(r) == 0: continue
        j = r[0][0]
        res.append((orders[j], drivers[i]))
        available[:, j] = 0
    return res



def best_dispatch(orders: list, drivers: list):
    orders.sort(key=lambda x: x.totalAmount)
    for order in orders:
        order.speed = 0
    np.random.shuffle(drivers)
    return list(zip(orders, drivers))