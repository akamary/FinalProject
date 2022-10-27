# Approximation algorithms for minimizing total busy time in parallel machines
## Final Project
<img width="600" src="https://github.com/akamary/FinalProject/blob/master/MyGIF.gif">

## Description
**The project divided into two phases**  
In our project we present a way in which we can use approximation algorithms for minimizing the busy time of machines that are scheduled with different jobs, while the jobs can work in a parallel manner. 
* **Phase A:**
On the first phase of our project we mostly summarized the article ["Minimizing total busy time in parallel scheduling with application to optical networks”](https://cs.idc.ac.il/~tami/Papers/IPDPS09.pdf) and wrote a book. For further information about our last semester project please check out Capstone Project Phase A.  
* **Phase B:** We wrote our second book and also build a desktop software for visualizing the outcome of the algorithms presented in the book. The software is written in Python and we used PyQt5 for designing the screens. We added graphs to visualize the FirstFit algorithm in several different ways. We also visualized the Special Cases section algorithms - Proper interval graphs and Bounded length algorithm. We added extra visualization of comparison between FirstFit and the optimal way to handle jobs for a very specific order of jobs (more on that in the User Documentation part of this book). Assides for the programming, we also researched the special cases section, we elaborated on the proof of the algorithms presented there, added examples and extensive clarifications. 


## In order to run this project, follow the instructions below:

* Install a Python IDE such as Pycharm or Spyder (We used Pycharm)
* Install Python 3.9
* Install packages: 
    * import random
    * import sys
    * from PyQt5 import QtWidgets
    * from PyQt5.QtWidgets import QApplication, QWidget, QDialog
    * from PyQt5.uic import loadUi
    * import pandas as pd
    * from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    * from matplotlib.figure import Figure
    * import matplotlib.pyplot as plt
    * import numpy as np
* Run the project!
