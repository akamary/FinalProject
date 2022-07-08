import random
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QLineEdit
from PyQt5.QtGui import QDoubleValidator, QValidator
from PyQt5.uic import loadUi
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from interval import Interval


# Main menu window
class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("MainMenu.ui", self)
        if QApplication.focusWidget() is not None:
            QApplication.focusWidget().clearFocus()
        self.pushButton.clicked.connect(self.gotoValueSelect)
        self.pushButton_4.clicked.connect(self.goToAveragePerformance)
        self.pushButton_2.clicked.connect(self.gotoSpecialCases)
        self.pushButton_5.clicked.connect(self.exitApp)

    def gotoValueSelect(self):
        valueSelect = ValueSelect()
        widget.addWidget(valueSelect)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def goToAveragePerformance(self):
        averagePerformance = AveragePerformance()
        widget.addWidget(averagePerformance)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotoSpecialCases(self):
        specialCases = SpecialCases()
        widget.addWidget(specialCases)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def exitApp(self):
        app.exit()


# Value selection window
class ValueSelect(QDialog):
    breakAllFlag = False
    firstTime = 0
    sizeOPT = np.ones(10, dtype=int)
    sizeFirstFit = np.ones(10, dtype=int)
    ratio = np.ones(10)
    flag = 0

    def __init__(self):
        super(ValueSelect, self).__init__()
        loadUi("ValueSelect.ui", self)
        self.textEdit.setTabChangesFocus(True)
        self.textEdit_2.setTabChangesFocus(True)
        self.textBrowser.hide()
        self.textBrowser_2.hide()
        self.pushButton_3.clicked.connect(self.gotoMainMenu)
        self.pushButton_2.clicked.connect(self.showGraph)

    def validating(self, m, x, window):
        valid = 0
        if window == "special":
            validation_rule = QDoubleValidator(1, 12, 0)
            validation_rule2 = QDoubleValidator(1, 100, 0)
        if window == "visual":
            validation_rule = QDoubleValidator(1, 100, 0)
            validation_rule2 = validation_rule
        if window == "avg":
            validation_rule = QDoubleValidator(2, 300, 0)
        if validation_rule.validate(m, 14)[0] == QValidator.Acceptable:
            valid += 1
            self.textBrowser.hide()
        else:
            self.textBrowser.show()
        if window == "visual" or window == "special":
            if validation_rule2.validate(x, 14)[0] == QValidator.Acceptable:
                valid += 1
                self.textBrowser_2.hide()
            else:
                self.textBrowser_2.show()
            if valid == 2:
                return True
        if window == "avg" and valid == 1:
            return True
        return False

    def gotoMainMenu(self):
        mainWindow = MainWindow()
        widget.addWidget(mainWindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def showGraph(self):
        m = self.textEdit.toPlainText()  # amount of jobs
        x = self.textEdit_2.toPlainText()  # amount of machines
        g = self.comboBox.currentText()  # parallel parameter
        if not self.validating(m, x, "visual"):
            return
        print("m =", m, ",x =", x, ",g =", g)
        results = Results()
        # starting the algorithm:
        randomArray = self.createRandomLengths()
        myMachines = self.firstFit(randomArray, x, m, g, "firstFit")
        if not myMachines is None:
            # here add the graph
            myPlot = Figure()
            myPlot.clear()
            for i in reversed(range(results.horizontalLayout_2.count())):
                results.horizontalLayout_2.itemAt(i).widget().setParent(None)
            canvas = FigureCanvas()
            myPlot = self.graphDisplay(myMachines, 3, 0)
            canvas = FigureCanvas(myPlot)
            results.horizontalLayout_2.addWidget(canvas)
            canvas.draw()
            myPlot = 1
            plt.close(3)
            results.textBrowser.hide()
        else:
            results.textBrowser.setPlainText("Not Enough Machines!")
            plt.close(3)
        widget.addWidget(results)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def createRandomLengths(self):
        m = int(self.textEdit.toPlainText())
        randomArray = np.random.randint(1, 20, m)
        print("Generated length of jobs (in hours): ", randomArray)
        return randomArray

    def sortLengths(self, array):
        array[::-1].sort()  # descending sort
        # print("jobs sorted in non-increasing order", randomArray)
        return array

    def createRandomIntervals(self, randomArray):
        intervals = np.zeros((randomArray.size, 2), dtype=int)
        for i in range(randomArray.size):
            start = np.random.randint(0, 24-randomArray[i])
            intervals[i][0] = start
            intervals[i][1] = start + randomArray[i]
        return intervals

    def firstFit(self, randomArray, x, m, g, flag):
        if flag == "firstFit":
            randomArray = ValueSelect.sortLengths(self, randomArray)
            intervals = ValueSelect.createRandomIntervals(self, randomArray)
        else:
            intervals = AveragePerformance.createIntervals(self, randomArray)
            intervals = AveragePerformance.sortIntervals(self, intervals)
        j = 0
        myJobs = []
        myMachines = []
        for i in range(int(x)):
            myMachines.append([])
        breakFlag = False
        # breakAllFlag = False
        clashByHour = np.zeros((int(x), 25))  # to check in each hour how many clashes we got - for each machine
        for i in range(randomArray.size):
            myJobs.append(Interval(intervals[i][0], intervals[i][1], i))
        myMachines[0].append((myJobs[0]))  # insert for job to first machine before loop.
        for l in range(myJobs[0].start, myJobs[0].end + 1):
            clashByHour[j, l] += 1
        # start inserting all other jobs
        for i in range(int(m)-1):  # jobs #Checking clashes
            while j < int(x):  # machines
                if not myMachines[j]:
                    counter = i
                else:
                    counter = myMachines[j][0].index
                for k in range(counter, i+1):  # from job 0 to curr job - check clashes of curr job with prev jobs
                    for l in range(myJobs[i+1].start, myJobs[i+1].end + 1):
                        clashByHour[j, l] += 1
                        if clashByHour[j, l] > int(g):
                            breakFlag = True  # move to next machine after finishing this inner loop
                    if not breakFlag:
                        myMachines[j].append(myJobs[i + 1])
                        j = int(x)  # stop the inner while
                        break
                    if breakFlag:  # remove those clashes cause this job won't be going into that machine.
                        for l in range(myJobs[i+1].start, myJobs[i+1].end + 1):
                            clashByHour[j, l] -= 1
                    if breakFlag:
                        breakFlag = False
                        if j < int(x) - 1:  # if we didn't reach the last machine yet.
                            j += 1
                            break
                        else:
                            print("Not enough machines")  # exit whole outer loop
                            self.breakAllFlag = True
                            return
            j = 0
        return myMachines

    def graphDisplay(self, myMachines, figNum, k):
        f = Figure()
        if figNum == 3 or figNum == 4:  # Value select or Special cases
            data_dict = {}
            machinesArr = []
            jobsStart = []
            jobsEnd = []
            for i in range(len(myMachines)):
                for j in range(len(myMachines[i])):
                    machinesArr.append("Machine " + str(i + 1) + " - Job " + str(myMachines[i][j].index + 1))
                    jobsStart.append(myMachines[i][j].start)
                    jobsEnd.append(myMachines[i][j].end)
                data_dict['jobs'] = machinesArr
                data_dict['lower'] = jobsStart
                data_dict['upper'] = jobsEnd
                dataset = pd.DataFrame(data_dict)
                f = plt.figure(figNum)
                for lower, upper, y in zip(dataset['lower'], dataset['upper'], range(len(dataset))):
                    plt.plot((lower, upper), (y, y), 'bo-')
                plt.yticks(range(len(dataset)), list(dataset['jobs']))
                plt.xticks(range(0, 24, 2))
                plt.xlabel("Time (Hour)")
        if figNum == 1 or figNum == 2:  # Average Performance
            if ValueSelect.firstTime == 0:
                sets = AveragePerformance.sets
                ValueSelect.sizeOPT = np.ones(sets, dtype=int)
                ValueSelect.sizeFirstFit = np.ones(sets, dtype=int)
                ValueSelect.ratio = np.ones(sets)
                ValueSelect.firstTime = 1
            counter = 0
            sets_for_t = float(AveragePerformance.sets)
            t = np.arange(0., sets_for_t, 1.)

            for i in range(len(myMachines)):
                if myMachines[i]:
                    counter += 1
            if figNum == 1:
                ValueSelect.sizeOPT[k] = counter
            else:
                ValueSelect.sizeFirstFit[k] = counter
            if k == AveragePerformance.sets - 1:
                ValueSelect.flag += 1
                if ValueSelect.flag > 1:
                    if AveragePerformance.machines_or_busy == "machines":
                        for i in range(k+1):
                            ValueSelect.ratio[i] = float(ValueSelect.sizeFirstFit[i]) / ValueSelect.sizeOPT[i]
                        plt.plot(t, ValueSelect.sizeOPT, 'r', label='OPT')
                        plt.plot(t, ValueSelect.sizeFirstFit, 'b', label='FirstFit')
                        plt.plot(t, ValueSelect.ratio, 'g', label='Ratio')
                        if k < 30:
                            xAxis = range(0, k + 1, 2)
                        if 60 > k >= 30:
                            xAxis = range(0, k + 1, 3)
                        if k >= 60:
                            xAxis = range(0, k + 1, 5)
                        if k >= 120:
                            xAxis = range(0, k + 1, 10)
                        yAxis = range(0, 24, 2)
                        plt.xlabel('Set Number')
                        plt.ylabel('Machines')
                        plt.yticks(yAxis)
                        plt.xticks(xAxis)
                        plt.legend(loc='center right', prop={'size': 15})
                        # plt.show()
                        # f = plt.figure(figNum)
                        f = plt.figure(1)
                    if AveragePerformance.machines_or_busy == "busyTime":
                        arrayForPlot = np.array([100] * (k + 1))
                        plt.plot(t, arrayForPlot, 'r', label='OPT')
                        for i in range(len(AveragePerformance.busyTime)):
                            AveragePerformance.busyTime[i] *= 100
                        plt.plot(t, AveragePerformance.busyTime, 'b', label='FirstFit')
                        if k < 30:
                            xAxis = range(0, k + 1, 2)
                        if 60 > k >= 30:
                            xAxis = range(0, k + 1, 3)
                        if k >= 60:
                            xAxis = range(0, k + 1, 5)
                        if k >= 120:
                            xAxis = range(0, k + 1, 10)
                        yAxis = range(30, 101, 5)
                        plt.xlabel('Set Number')
                        plt.ylabel('Busy Time Percent')
                        plt.yticks(yAxis)
                        plt.xticks(xAxis)
                        plt.legend(loc='center right', prop={'size': 15})
                        f = plt.figure(1)

        return f


# Average performance window
class AveragePerformance(QDialog):
    sets = 0
    machines_or_busy = "machines"  # "machines" or "busyTime"
    busyTime = []

    def __init__(self):
        super(AveragePerformance, self).__init__()
        loadUi("AveragePerformance.ui", self)
        self.textEdit.setTabChangesFocus(True)
        self.textBrowser.hide()
        self.pushButton_3.clicked.connect(self.machinesClicked)  # Show Machines
        self.pushButton_4.clicked.connect(self.busyClicked)  # Show Busy Time
        self.pushButton_5.clicked.connect(self.gotoMainMenu)

    def machinesClicked(self):
        AveragePerformance.machines_or_busy = "machines"
        self.goToResults()

    def busyClicked(self):
        AveragePerformance.machines_or_busy = "busyTime"
        self.goToResults()

    def goToResults(self):  # compare to optimum
        AveragePerformance.sets = self.textEdit.toPlainText()  # amount of sets
        if not ValueSelect.validating(self, AveragePerformance.sets, -1, "avg"):
            return
        AveragePerformance.sets = int(AveragePerformance.sets)
        AveragePerformance.busyTime = [0] * self.sets
        g = 2
        x = 50  # max machines needed
        results = Results()
        myPlot = Figure()
        myPlot.clear()
        for i in reversed(range(results.horizontalLayout_2.count())):
            results.horizontalLayout_2.itemAt(i).widget().setParent(None)
        canvas = FigureCanvas()
        for i in range(self.sets):  # loop by amount of sets
            array = self.createLengths()  # length of jobs
            m = array.size
            myMachines = self.assignJobsToMachines(array, x, m)
            myMachinesWithFirstFit = ValueSelect.firstFit(self, array, x*3, m, g, "notFirstFit")
            AveragePerformance.busyTime[i] = self.calculateBusyTime(myMachinesWithFirstFit)  # busy time per set.
            myPlot = ValueSelect.graphDisplay(self, myMachines, 1, i)
            myPlot = ValueSelect.graphDisplay(self, myMachinesWithFirstFit, 2, i)
        # myPlot.show()
        ValueSelect.flag = 0
        avg = 0.0
        for i in range(AveragePerformance.sets):
            if AveragePerformance.machines_or_busy == "machines":
                avg = avg + ValueSelect.ratio[i]
            if AveragePerformance.machines_or_busy == "busyTime":
                avg = avg + AveragePerformance.busyTime[i]
        avg = avg / AveragePerformance.sets
        avg = "{:.3f}".format(avg)
        if AveragePerformance.machines_or_busy == "machines":
            results.textBrowser.append(str(avg))
        if AveragePerformance.machines_or_busy == "busyTime":
            results.textBrowser.setPlainText("Average Busy Time: " + str(avg) + "%")
        # canvas:
        canvas = FigureCanvas(myPlot)
        results.horizontalLayout_2.addWidget(canvas)
        canvas.draw()
        myPlot = 1
        plt.close(1)
        plt.close(2)
        results.label_2.setText("Average Performance")
        ValueSelect.firstTime = 0
        widget.addWidget(results)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def createLengths(self):
        array = []
        flag = True
        counter = 0
        for i in range(100):
            array.append([])
        for i in range(100):
            while flag:
                r = random.randint(1, 12)  # can play with this, to switch a bit the average ratio
                counter += r
                if counter < 24:
                    array[i].append(r)
                else:
                    array[i].append(24-counter+r)
                    counter = 0
                    flag = False
            flag = True
        c = random.randint(0, 99)
        array2 = np.array(array[c])
        myRange = random.randint(5, 29)
        for i in range(myRange):  # try to change to 9 or 19, maybe change plots, so it can fit there...
            c = random.randint(1, 99)
            array3 = np.array(array[c])
            array2 = np.concatenate((array2, array3))

        print("Generated length of jobs (in hours): ", array2)
        return array2

    def createIntervals(self, array):
        intervals = np.zeros((array.size, 2), dtype=int)
        curr_length = array[0]
        for i in range(array.size - 1):
            start = curr_length - array[i]
            end = curr_length
            curr_length += array[i+1]
            intervals[i][0] = start
            intervals[i][1] = end
            if end >= 24:
                curr_length = array[i+1]
        start = curr_length - array[array.size - 1]  # last iteration
        end = curr_length
        intervals[i+1][0] = start
        intervals[i+1][1] = end
        return intervals

    def assignJobsToMachines(self, array, x, m):
        intervals = self.createIntervals(array)
        j = 0
        myJobs = []
        myMachines = []
        for i in range(int(x)):
            myMachines.append([])
        for i in range(array.size):
            myJobs.append(Interval(intervals[i][0], intervals[i][1], i))
        myMachines[0].append((myJobs[0]))
        for i in range(int(x)):  # machines
            parallelCounter = 0
            counter = 0
            while j < int(m) - 1:  # jobs
                myMachines[i].append(myJobs[j + 1])
                j += 1
                if myJobs[j].end == 24:
                    parallelCounter += 1
                    if parallelCounter == 2:  # represents the g
                        break
                counter += 1
        return myMachines

    def sortIntervals(self, intervals):
        length = 0
        size = intervals.size
        zeros = np.zeros(int(size / 2)).astype(int)
        intervals = np.insert(intervals, 2, zeros, axis=1)
        for i in range(int(size / 2)):
            length = intervals[i][1] - intervals[i][0]
            intervals[i][2] = length
        intervals = intervals[intervals[:, 2].argsort()[::-1]]
        return intervals

    def calculateBusyTime(self, machines):
        busyTime = 0
        counter = 0
        amountOfMachines = 0
        for i in range(len(machines)):
            if len(machines[i]) == 0:
                amountOfMachines = i
                break
            for j in range(len(machines[i])):
                counter += machines[i][j].length
            busyTime += float(counter)
            counter = 0
        busyTime = float(busyTime / (48.0 * amountOfMachines))  # 48 is 24*2 since g is equal to 2, and we have 24 hours
        return busyTime

    def gotoMainMenu(self):
        mainWindow = MainWindow()
        widget.addWidget(mainWindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# Special cases window
class SpecialCases(QDialog):
    def __init__(self):
        super(SpecialCases, self).__init__()
        loadUi("SpecialCases.ui", self)
        self.textEdit.setTabChangesFocus(True)
        self.textEdit_2.setTabChangesFocus(True)
        self.textBrowser.hide()
        self.textBrowser_2.hide()
        self.pushButton_5.clicked.connect(self.gotoMainMenu)
        self.pushButton_3.clicked.connect(self.properIntervalGraphs)

    def gotoMainMenu(self):
        mainWindow = MainWindow()
        widget.addWidget(mainWindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def properIntervalGraphs(self):
        results = Results()
        g = self.comboBox.currentText()  # parallel parameter
        m = self.textEdit.toPlainText()  # jobs
        x = self.textEdit_2.toPlainText()  # machines
        if not ValueSelect.validating(self, m, x, "special"):
            return
        g = int(g)
        m = int(m)
        x = int(x)
        # starting the algorithm:
        randomArray = self.createRandomLengths()
        while True:
            intervals = self.createRandomIntervals(randomArray)
            if intervals[m-1][1] != 0:
                break
        intervals = self.sortIntervals(intervals)
        myMachines = self.nextFit(intervals, m, g, x)
        if myMachines is not None:
            # draw
            myPlot = Figure()
            myPlot.clear()
            for i in reversed(range(results.horizontalLayout_2.count())):
                results.horizontalLayout_2.itemAt(i).widget().setParent(None)
            canvas = FigureCanvas()
            myPlot = ValueSelect.graphDisplay(self, myMachines, 4, 0)
            canvas = FigureCanvas(myPlot)
            results.horizontalLayout_2.addWidget(canvas)
            canvas.draw()
            myPlot = 1
            plt.close(4)
            results.textBrowser.hide()
        else:
            results.textBrowser.setPlainText("Not Enough Machines!")
        results.label_2.setText("Proper Interval Graphs")
        widget.addWidget(results)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def createRandomLengths(self):
        m = int(self.textEdit.toPlainText())
        randomArray = np.random.randint(1, 12, m)
        print("Generated length of jobs (in hours): ", randomArray)
        return randomArray

    def createRandomIntervals(self, randomArray):
        counter = 0
        breakFlag = 0
        intervals = np.zeros((randomArray.size, 2), dtype=int)
        i = 0
        while i < randomArray.size:
            counter += 1
            start = np.random.randint(0, 24 - randomArray[i])
            for j in range(intervals.size):
                if intervals[j][1] != 0:
                    # make sure we're creating proper interval graphs
                    if (start >= intervals[j][0] and start + randomArray[i] <= intervals[j][1]) or (intervals[j][0] >= start and intervals[j][1] <= start + randomArray[i]):
                        breakFlag = 1
                        break
                else:
                    break
            if breakFlag == 0:
                intervals[i][0] = start
                intervals[i][1] = start + randomArray[i]
                i += 1
            breakFlag = 0
            if counter >= 2000:
                counter = 0
                print("Do another iteration")
                break
        return intervals

    def sortIntervals(self, intervals):
        # intervals = intervals[intervals[:, 0].argsort()]  # sort by column 0 : start
        ind = np.lexsort((intervals[:, 1], intervals[:, 0]))
        return intervals[ind]

    def nextFit(self, intervals, m, g, x):
        j = 0
        breakInner = 0
        myJobs = []
        myMachines = []
        for i in range(x):
            myMachines.append([])
        breakFlag = False
        clashByHour = np.zeros((x, 25))  # to check in each hour how many clashes we got - for each machine
        for i in range(int(intervals.size / 2)):
            myJobs.append(Interval(intervals[i][0], intervals[i][1], i))
        myMachines[0].append((myJobs[0]))  # insert for job to first machine before loop.
        for l in range(myJobs[0].start, myJobs[0].end + 1):
            clashByHour[j, l] += 1
        # start inserting all other jobs
        for i in range(x):  # machines #Checking clashes
            while j < m-1:  # jobs
                if not myMachines[i]:
                    counter = j
                else:
                    counter = myMachines[i][0].index
                for k in range(counter, j + 1):  # from first job in machine to curr job - check clashes of curr job with prev jobs
                    for l in range(myJobs[j + 1].start, myJobs[j + 1].end + 1):
                        clashByHour[i, l] += 1
                        if clashByHour[i, l] > int(g):
                            breakFlag = True  # move to next machine after finishing this inner loop
                    if not breakFlag:
                        myMachines[i].append(myJobs[j + 1])
                        j += 1
                        break
                    if breakFlag:  # remove those clashes cause this job won't be going into that machine.
                        for l in range(myJobs[j + 1].start, myJobs[j + 1].end + 1):
                            clashByHour[i, l] -= 1
                        breakFlag = False
                        if i < x - 1:  # if we didnt yet reach the last machine.
                            i += 1  # move to next machine
                            break
                        else:
                            print("Not enough machines")  # exit whole outer loop
                            self.breakAllFlag = True
                            return
                if breakFlag:
                    breakFlag = False
            if j == m - 1:
                break

        return myMachines


# the window at which the graph will be displayed
class Results(QDialog):
    def __init__(self):
        super(Results, self).__init__()
        loadUi("Results.ui", self)
        QApplication.focusWidget().clearFocus()
        self.pushButton_3.clicked.connect(self.gotoMainMenu)

    def gotoMainMenu(self):
        mainWindow = MainWindow()
        widget.addWidget(mainWindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)


app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
mainWindow = MainWindow()
widget.addWidget(mainWindow)
widget.showFullScreen()
# widget.setFixedHeight(1080)
# widget.setFixedWidth(1920)
widget.setWindowTitle("First Fit Algorithm")
widget.show()
app.exec()
