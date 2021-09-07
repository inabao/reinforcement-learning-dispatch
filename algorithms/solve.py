import numpy as np

import time
from setting import *
from reinforcement import stateValueInit, stateValueSave, assess

from datadeal.problem import ProblemInstance
from algorithms.dispatch import random_dispatch, best_dispatch, bigrah_dispatch, reinforce


def solve(problem: ProblemInstance, evaluate=False):
    currentTime = problem.startTime
    index = 0
    if algorithm[0] != "r" and algorithm[0] != "b":
        stateValueInit()
    while problem.waitOrder and currentTime < problem.endTime:
        orders, drivers = problem.batch(currentTime)
        if algorithm == "random":
            solution = random_dispatch(orders, drivers)
        elif algorithm == "best":
            solution = best_dispatch(orders, drivers)
        elif algorithm == "bigraph":
            solution = bigrah_dispatch(orders, drivers)
        elif algorithm == "bigraph_income":
            solution = bigrah_dispatch(orders, drivers, income=True)
        else:
            solution = reinforce(orders, drivers, index)
        for order, driver in solution:
            driver.serve(order, currentTime)
        if evaluate:
            assess(solution, index)
        currentTime += fragment
        index += 1
    if evaluate:
        stateValueSave()
