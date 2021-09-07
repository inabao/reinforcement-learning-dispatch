import time
import numpy as np
from setting import *
np.random.seed(seed)


class Order:
    def __init__(self, dataLine):
        dataList = dataLine.strip().split(',')
        self.pickTime = time.mktime(time.strptime(dataList[1], '%Y-%m-%d %H:%M:%S'))
        self.dropoffTime = time.mktime(time.strptime(dataList[2], '%Y-%m-%d %H:%M:%S'))
        self.passengerCount = int(dataList[3])
        self.tripDistance = float(dataList[4])
        self.pickX = float(dataList[5])
        self.pickY = float(dataList[6])
        try:
            self.dropX = float(dataList[9])
            self.dropY = float(dataList[10])
        except:
            self.dropY = self.pickY
            self.dropX = self.pickX
        self.absluteDistance = abs(self.pickX - self.dropX) + abs(self.pickY - self.dropY)

        if (self.dropoffTime - self.pickTime) == 0:
            self.speed = 0.00009
        else:
            self.speed = self.absluteDistance / (self.dropoffTime - self.pickTime)
            if self.speed > 0.00015: self.speed = 0.00015
            if self.speed < 0.00006: self.speed = 0.00006
        self.deadline = (self.absluteDistance / self.speed) * 1.5 + self.durable
        self.totalAmount = float(dataList[-1])
        self.durable = np.random.randint(200) + 200
        self.available = True

    def __add__(self, order):
        self.deadline = min(self.deadline, order.deadline)
        self.durable = min(self.durable, order.durable)
        self.totalAmount = self.totalAmount + order.totalAmount
        self.speed = (self.absluteDistance + order.absluteDistance) / (self.dropoffTime + order.dropoffTime - self.pickTime - order.pickTime)


    def judgeLocation(self, range_xy):
        if range_xy[0] < self.pickX < range_xy[1] and range_xy[2] < self.pickY < range_xy[3] and range_xy[
            0] < self.dropX < range_xy[1] and range_xy[2] < self.dropY < range_xy[3]:
            return True
        return False

    def getPickLocation(self):
        return self.pickX, self.pickY

    def getDropLocation(self):
        return self.dropX, self.dropY

    def toString(self, id, pickRegin, dropRegin):
        return ",".join([str(id), str(pickRegin), str(dropRegin), str(self.pickX), str(self.pickY), str(self.dropX),
                         str(self.dropY),
                         str(self.pickTime), str(self.dropoffTime),
                         str(self.totalAmount), str(self.tripDistance), str(np.random.randint(10) + 4)])


class Driver:
    def __init__(self, location):
        self.severedOrder = []
        self.x, self.y = location
        self.relaxTime = 0


    def isAccept(self, order: Order):
        if (abs(self.x - order.pickX) + abs(self.y - order.pickY)) / order.speed > takeTime:
            return False
        return True

    def serve(self, order: Order, currentTime):
        order.available = False
        self.severedOrder.append(order)
        pickTime = 0 if order.speed == 0 else (abs(self.x - order.pickX) + abs(self.y - order.pickY)) / order.speed
        self.relaxTime = currentTime + order.dropoffTime - order.pickTime + pickTime
        # sums = reinforcement.incomeRate.averageReward * reinforcement.incomeRate.roundCount
        # reinforcement.incomeRate.roundCount += (self.relaxTime - currentTime) // fragment
        # sums += order.totalAmount
        # reinforcement.incomeRate.averageReward = sums / reinforcement.incomeRate.roundCount
        #
        #



if __name__ == '__main__':
    with open(data_path, "r", encoding="utf8") as f:
        content = f.readline()

    order = Order(content)
    print(order)
