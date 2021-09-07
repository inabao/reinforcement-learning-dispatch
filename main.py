import time
from datetime import datetime

from setting import *
from datadeal.problem import ProblemInstance
from algorithms.solve import solve

def main():
    problem = ProblemInstance(data_path, driverCount)
    t1 = time.time()
    solve(problem, evaluate=EVALUATE)
    t2 = time.time()
    serveredOrder = []
    for driver in problem.drivers:
        serveredOrder.extend(driver.severedOrder)

    count = 0
    totalAmount = 0
    serveTime = 0
    for order in serveredOrder:
        count += 1
        totalAmount += order.totalAmount
        serveTime += order.dropoffTime - order.pickTime
    d = datetime.now()
    with open("result/%s_%d_%d_%d_%s.txt" % (algorithm, month, day, fragment, d.strftime("%d-%H-%M")), "w", encoding="utf8") as f:
        f.write("execute:%f  count:%d  time:%f  income:%f" % (t2-t1, count, serveTime, totalAmount))


if __name__ == '__main__':
    main()