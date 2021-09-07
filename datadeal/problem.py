import numpy as np
from datadeal.orderAndDriver import Order, Driver
from setting import *
import time
import os
import pickle
np.random.seed(seed)


class ProblemInstance:
    def __init__(self, orderPath, driverCount):
        # load orders
        self.waitOrder = []
        if os.path.exists("tmpData/%d_%d.pl" % (month, day)):
            with open("tmpData/%d_%d.pl" % (month, day), "rb") as f:
                self.waitOrder = pickle.load(f)
        else:
            with open(orderPath, "r", encoding="utf8") as f:
                content = f.readline()
                while content != "":
                    order = Order(content)
                    if order.judgeLocation(XREGION + YREGION):
                        self.waitOrder.append(order)
                    content = f.readline()
            if not os.path.exists("tmpData"):
                os.makedirs("tmpData")
            with open("tmpData/%d_%d.pl" % (month, day), "wb") as f:
                pickle.dump(self.waitOrder, f)

        # self.waitOrder.sort(key=lambda x: x.pickTime)
        self.startTime = self.waitOrder[0].pickTime
        self.endTime = self.startTime + 60 * 60 * 24
        # load drivers
        select = np.random.randint(len(self.waitOrder), size=driverCount)
        self.drivers = [Driver(self.waitOrder[i].getPickLocation()) for i in select]

    def batch(self, currentTimestamp):
        ords = iter(self.waitOrder)
        single_order = next(ords)
        orders = []
        while single_order.pickTime < currentTimestamp:
            if single_order.pickTime + single_order.durable <= currentTimestamp or not single_order.available:
                self.waitOrder.remove(single_order)
            else:
                orders.append(single_order)
            single_order = next(ords)
        drivers = list(filter(lambda x: x.relaxTime < currentTimestamp, self.drivers))
        return orders, drivers

if __name__ == '__main__':
    problemInstance = ProblemInstance(data_path, 1000)
    print()


