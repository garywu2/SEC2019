class Destination:
    def __init__(self, theid, name, distance):
        self.theid = theid
        self.name = name
        self.distance = distance
        self.traveltime = distance * 2
