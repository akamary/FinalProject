class Interval:
    def __init__(self, start, end, index):
        self.start = start
        self.end = end
        self.length = end - start
        self.index = index
        self.toString = "Start = " + str(self.start) + ", End = " + str(self.end) + "."
