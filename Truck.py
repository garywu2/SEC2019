class Truck:
    def __init__(self, theid, initdis, speed, capacity, fueleco, delelicate, refrig):
        self.theid = theid
        self.initDis = initdis
        self.speed = speed
        self.capacity = capacity
        self.fuelEco = fueleco
        self.delelicate = delelicate
        self.refrig = refrig
        self.destination = 0
        self.avilable = True
        self.location = 0
        self.depatureTime = 0

    def gettimereturn(self):
        #if not self.avilable:
        return self.destination * 2 / self.speed + self.depatureTime

    def timetodest(self, destination):
        if destination == 0:
            return 0
        return destination.distance / self.speed

    def setdestination(self, destination):
        self.destination = destination












