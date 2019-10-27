class Package:
    def __init__(self, theid, arrivetime, destination, expiry, weight, delicate, cold):
        self.theid = theid
        self.arrivetime = arrivetime
        self.delicate = delicate
        self.weight = weight
        self.destination = destination
        self.expiry = expiry
        self.refrig = cold

    def getmaxdeparture(self, truck):
       return self.expiry - truck.timetodest(self.destination)