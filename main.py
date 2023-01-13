from PyQt6.QtWidgets import *
from PyQt6.QtGui import * 
import sys
import xlrd
from ctypes import *
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
import random

tab_orders = []#will contain the numbers of items for each order
pauseDuration = -1
pauseStart = -1

class Window(QWidget):
    """
    This is our main class, it will contain the GUI and it will handle the differents input to display the gantt chart at the end.
    This class extends from Qwidget so it will have the same properties.
    """
    def __init__(self):
        """
        What we do here is mostly initializing the interface. We create our components (layout and widgets).
        When we create interactive components as a button for exemple, we link a function that will be called when we interact with the widget.
        """
        super().__init__()
        self.m1Duration = []
        self.m2Duration = []
        self.precision = 100
        self.orderWindow = None
        self.popup = None
        self.loadFromExcel = True
        self.pauseDuration = -1
        self.pauseStart = -1
        #self.setWindowIcon
        self.excelPath = ""
        self.formulaM1 = ""
        self.formulaM2 = ""
        self.setWindowTitle("Task scheduling (two machines)")
        
        self.setGeometry(0, 0, 800, 400)
        self.mainLayout = QHBoxLayout()#Separate the window horizontally
        settingsBoxContainer = QWidget()
        settingsBox = QVBoxLayout()
        labelSettings = QLabel("Settings : ")#Title of our section
        labelSettings.setFont(QFont("Arial", 15))
        settingsBox.addWidget(labelSettings)

        dataGroup = QGroupBox("Data : ")#Group of widgets for choosing excel or typing by hand
        layoutDataGroup = QGridLayout()
        layoutDataGroup.addWidget(QLabel("Load data from excel"), 0, 0, 1, 1)
        self.checkExcel = QCheckBox()
        self.checkExcel.setChecked(True)
        self.checkExcel.stateChanged.connect(lambda: self.checkboxChange())
        layoutDataGroup.addWidget(self.checkExcel, 0, 1, 1, 1)
        self.excelButton = QPushButton("Load from excel")
        self.excelButton.clicked.connect(lambda: self.click_excel())
        layoutDataGroup.addWidget(self.excelButton, 1, 0, 2, 1)
        self.filenameLabel = QLabel("")
        layoutDataGroup.addWidget(self.filenameLabel, 2, 0, 2, 1)
        self.dataButton = QPushButton("Type data")
        self.dataButton.setDisabled(True)
        self.dataButton.clicked.connect(lambda: self.click_data())
        layoutDataGroup.addWidget(self.dataButton, 3, 0, 2, 1)
        dataGroup.setMinimumHeight(150)
        dataGroup.setLayout(layoutDataGroup)
        settingsBox.addWidget(dataGroup)

        algoGroup = QGroupBox("Algorithm : ")
        layoutAlgoGroup = QVBoxLayout()
        self.johnsonBtn = QRadioButton("Johnson algorithm")
        self.johnsonBtn.setChecked(True)
        self.heuristicBtn = QRadioButton("Heuristic algorithm")
        layoutAlgoGroup.addWidget(self.johnsonBtn)
        layoutAlgoGroup.addWidget(self.heuristicBtn)
        algoGroup.setLayout(layoutAlgoGroup)
        settingsBox.addWidget(algoGroup)

        durationGroup = QGroupBox("Duration for each machine (minutes) : ")
        layoutDuration = QGridLayout()
        layoutDuration.addWidget(QLabel("n : number of scooters\n '//' : euclidian division\n '%' : modulo"), 0, 0, 1, 2)
        layoutDuration.addWidget(QLabel("Duration M1 : "), 1, 0, 1, 1)
        self.entryM1 = QLineEdit()
        self.entryM1.setText("20*((n-1)//5 + 1)")
        layoutDuration.addWidget(self.entryM1, 1, 1, 1, 1)
        layoutDuration.addWidget(QLabel("Duration M2 : "), 2, 0, 1, 1)
        self.entryM2 = QLineEdit()
        self.entryM2.setText("5*n")
        layoutDuration.addWidget(self.entryM2, 2, 1, 1, 1)
        durationGroup.setLayout(layoutDuration)
        settingsBox.addWidget(durationGroup)

        self.goBtn = QPushButton("Go")
        self.goBtn.clicked.connect(lambda: self.validate())
        settingsBox.addWidget(self.goBtn)

        settingsBox.addStretch()
        settingsBoxContainer.setLayout(settingsBox)
        settingsBoxContainer.setMaximumWidth(350)
        self.mainLayout.addWidget(settingsBoxContainer)
        self.table = TableWidget(self)#Our table widget
        self.mainLayout.addWidget(self.table)
        self.setLayout(self.mainLayout)
        self.show()

    def emptyData(self):
        """
        In this function, we empty the arrays in wich we store the orders and the processing times.
        We also reset the values for the beginning and duration of the pause.
        """
        global tab_orders, pauseDuration, pauseStart
        tab_orders=[]
        pauseDuration = -1
        pauseStart = -1
        self.m1Duration = []
        self.m2Duration = []
        self.pauseStart = -1
        self.pauseDuration = -1

    def validate(self):
        """
        This function is called when we click on "go" to create the gantt.
        If we chose to read data on an excel file, we will try and read it. If we typed data by hand, we will also check that everything is correct (int given, good date format).
        We try to get the time for each task with the formula. If there is an error in the process, we will show a popup with a message.
        Else, we will call the functions to draw the gantt
        """
        global tab_orders, pauseDuration, pauseStart
        print("Validating")
        if self.loadFromExcel == True:#We choosed to load data using an excel file
            try:
                path = self.excelPath.replace("/", "\\")
                excel_workbook = xlrd.open_workbook(path)
                excel_worksheet = excel_workbook.sheet_by_index(0)
                tab_orders=[]
                for rows in range(1,excel_worksheet.nrows) :
                    tab_orders.append(int(excel_worksheet.cell_value(rows, 1)))
                excel_worksheet = excel_workbook.sheet_by_index(1)
                a = xlrd.xldate_as_datetime(excel_worksheet.cell_value(0, 1), 0)
                self.pauseStart = a.hour * 60 + a.minute
                a = xlrd.xldate_as_datetime(excel_worksheet.cell_value(1, 1), 0)
                self.pauseDuration = a.hour * 60 + a.minute
            except Exception as e:
                print(e)
                self.infoPopup("Error reading the excel file")
                return -1
        else:#Loading from data window
            if tab_orders == []:#tab is empty
                self.infoPopup("Please enter some informations about the order")
                return -1
            else:
                
                if pauseStart != -1 and pauseDuration != -1:#
                    self.pauseStart = pauseStart
                    self.pauseDuration = pauseDuration
                else:
                    self.infoPopup("Please specify a beginning and a duration")
                    return -1
                
        #If we reach here it means that we had no problem, we can compute and display the gantt
        if self.m1Duration == []:#We compute for the first time
            for i in tab_orders:
                n = i
                try:
                    self.m1Duration.append(int(eval(str(self.entryM1.text()))))#We compute the duration of each machine using the formula typed in the input
                    self.m2Duration.append(int(eval(str(self.entryM2.text()))))
                except Exception as e:
                    print(e)
                    self.infoPopup("Error in the formulas of the duration")
                    return -1
        try:
            if self.johnsonBtn.isChecked() == False:#We will use our heuristics algorithm
                print("Heuristic algorithm")
                m1=(c_int * len(tab_orders))(*self.m1Duration)
                m2=(c_int * len(tab_orders))(*self.m2Duration)
                p = (c_int*(len(tab_orders)+2))()#We add 1 to the size because last elemend is index of the middle
                lib = CDLL("./main.dll")
                lib.final_sort.argtypes = [POINTER(c_int),POINTER(c_int),POINTER(c_int), c_int, c_int, c_int, c_int]
                lib.final_sort.restype = None
                lib.final_sort(m1,m2,p,len(tab_orders), self.pauseStart, self.pauseDuration, self.precision)
                p = list(p)
                print("Result")
                print(p)
                totalDuration = p[-1]#we get index middle and duration then delete it from the task list
                indexMiddle = p[-2]
                p.pop(-1)
                p.pop(-1)
                print("Draw gantt")
                self.drawGanttTask(p, indexMiddle, totalDuration)
                self.drawGanttMachine(p, indexMiddle, totalDuration)
            else:#We use modified johnson
                print("Johnson algorithm")

                m1=(c_int * len(tab_orders))(*self.m1Duration)
                m2=(c_int * len(tab_orders))(*self.m2Duration)
                p = (c_int*(len(tab_orders)+2))()#We add 1 to the size because last elemend is index of the middle
                lib = CDLL("./main.dll")
                lib.final_johnson.argtypes = [POINTER(c_int),POINTER(c_int),POINTER(c_int), c_int, c_int, c_int]
                lib.final_johnson.restype = None
                lib.final_johnson(m1,m2,p,len(tab_orders), self.pauseStart, self.pauseDuration)
                p = list(p)
                print("Result")
                print(p)
                totalDuration = p[-1]#we get index middle and duration then delete it from the task list
                indexMiddle = p[-2]
                p.pop(-1)
                p.pop(-1)
                print("Draw gantt")
                self.drawGanttTask(p, indexMiddle, totalDuration)
                self.drawGanttMachine(p, indexMiddle, totalDuration)
        except Exception as e:
            print(e)
            self.infoPopup("An error occured")
                
    def drawGanttTask(self, tab, indexMiddle, totalDuration):
        """
        We will generate an image file with the gantt using the given parameters.
        In this gantt, we have the tasks on the y axis and the duration on the x axis.
        """
        global pauseStart, pauseDuration
        fig, gnt = plt.subplots() 
        # Setting Y-axis limits
        gnt.set_ylim(0, 5*(len(tab)+2))

        # Setting X-axis limits
        gnt.set_xlim(0, totalDuration*1.1)

        # Setting labels for x-axis and y-axis
        gnt.set_xlabel('minutes since start')
        gnt.set_ylabel('')

        # Setting ticks on y-axis
        ticks=[]
        ticksNames = []
        for i in range(5,(len(tab)+2)*5,5):#Adding one tick for the pause
            ticks.append(int(i))
            ticksNames.append("Tasks " + str(int(i/5)))
        ticksNames[-1] = "Pause"
        gnt.set_yticks(ticks)
        # Labelling tickes of y-axis
        gnt.set_yticklabels(ticksNames)
        # Setting graph attribute
        gnt.grid(True)
        # Drawing the Gantt
        timeM1=0
        timeM2 = 0
        for i in range(0, indexMiddle):
            currentTask = tab[i] + 1
            gnt.broken_barh([(timeM1, self.m1Duration[tab[i]])], ((5*currentTask)-2, 4), facecolors =('orange'))
            timeM1+=self.m1Duration[tab[i]]
            if timeM2 < timeM1 :
                gnt.broken_barh([(timeM1, self.m2Duration[tab[i]])], ((5*currentTask)-2, 4), facecolors =('red'))
                timeM2 = timeM1 + self.m2Duration[tab[i]]
            else :
                gnt.broken_barh([(timeM2, self.m2Duration[tab[i]])], ((5*currentTask)-2, 4), facecolors =('red'))
                timeM2+=self.m2Duration[tab[i]]
        #Drawing pause
        gnt.broken_barh([(self.pauseStart, self.pauseDuration)], ((5*(len(tab)+1))-2, 4), facecolors =('blue'))
        if self.pauseDuration != 0:
            timeM1 = self.pauseStart + self.pauseDuration
        for i in range(indexMiddle, len(tab)):
            currentTask = tab[i] + 1
            gnt.broken_barh([(timeM1, self.m1Duration[tab[i]])], ((5*currentTask)-2, 4), facecolors =('orange'))
            timeM1+=self.m1Duration[tab[i]]
            if timeM2 < timeM1 :
                gnt.broken_barh([(timeM1, self.m2Duration[tab[i]])], ((5*currentTask)-2, 4), facecolors =('red'))
                timeM2 = timeM1 + self.m2Duration[tab[i]]
            else :
                gnt.broken_barh([(timeM2, self.m2Duration[tab[i]])], ((5*currentTask)-2, 4), facecolors =('red'))
                timeM2+=self.m2Duration[tab[i]]

        plt.savefig("gantt1.png")
        self.table.showTask("gantt1.png", totalDuration, 1)

    def drawGanttMachine(self, tab, indexMiddle, totalDuration):
        """
        This method also generates a gantt in an image file but we have the two machines on the y axis.
        This allows us to see the process from the machine point of view.
        """
        global pauseStart, pauseDuration
        fig, gnt = plt.subplots()
        # Setting Y-axis limits
        gnt.set_ylim(0, 17)

        # Setting X-axis limits
        gnt.set_xlim(0, totalDuration*1.1)

        # Setting labels for x-axis and y-axis
        gnt.set_xlabel('minutes since start')
        gnt.set_ylabel('')

        # Setting ticks on y-axis
        ticks=[5, 10, 15]
        ticksNames = ["Machine 1", "Machine 2", "Pause"]
        gnt.set_yticks(ticks)
        # Labelling tickes of y-axis
        gnt.set_yticklabels(ticksNames)
        # Setting graph attribute
        gnt.grid(True)
        # Drawing the Gantt
        timeM1=0
        timeM2 = 0
        color = [random.uniform(0, 1) for i in range(3)]
        for i in range(0, indexMiddle):
            
            gnt.broken_barh([(timeM1, self.m1Duration[tab[i]])], (3, 4), facecolors =tuple(color))
            timeM1+=self.m1Duration[tab[i]]
            if timeM2 < timeM1 :
                gnt.broken_barh([(timeM1, self.m2Duration[tab[i]])], (8, 4), facecolors =tuple(color))
                timeM2 = timeM1 + self.m2Duration[tab[i]]
            else :
                gnt.broken_barh([(timeM2, self.m2Duration[tab[i]])], (8, 4), facecolors =tuple(color))
                timeM2+=self.m2Duration[tab[i]]
            color = [random.uniform(0, 1) for i in range(3)]
        #Drawing pause
        gnt.broken_barh([(self.pauseStart, self.pauseDuration)], (13, 4), facecolors =("black"))
        if self.pauseDuration != 0:
            timeM1 = self.pauseStart + self.pauseDuration
        for i in range(indexMiddle, len(tab)):
            gnt.broken_barh([(timeM1, self.m1Duration[tab[i]])], (3, 4), facecolors =tuple(color))
            timeM1+=self.m1Duration[tab[i]]
            if timeM2 < timeM1 :
                gnt.broken_barh([(timeM1, self.m2Duration[tab[i]])], (8, 4), facecolors =tuple(color))
                timeM2 = timeM1 + self.m2Duration[tab[i]]
            else :
                gnt.broken_barh([(timeM2, self.m2Duration[tab[i]])], (8, 4), facecolors =tuple(color))
                timeM2+=self.m2Duration[tab[i]]
            color = [random.uniform(0, 1) for i in range(3)]

        plt.savefig("gantt2.png")
        self.table.showTask("gantt2.png", totalDuration, 2)


    def infoPopup(self, text):
        """
        Displays a popup with the message as parameter
        """
        self.popup = QMessageBox()
        self.popup.setIcon(QMessageBox.Icon.Information)
        self.popup.setText(text)
        self.popup.setWindowTitle("Information")
        self.popup.show()

    def checkboxChange(self):
        """
        Called everytime we change the state of the checkbox, disables the according buttons
        (if we click on load excel file, the button with excel will be clickable and the button to load data manually will be disabled)
        """
        if self.checkExcel.isChecked() == True:
            self.loadFromExcel = True
            self.dataButton.setDisabled(True)
            self.excelButton.setDisabled(False)
        else:
            self.loadFromExcel = False
            self.dataButton.setDisabled(False)
            self.excelButton.setDisabled(True)
        
    def click_excel(self):
        """
        Is called when we click on the excel button.
        Opens a popup to choose an excel file
        """
        self.emptyData()
        print("Clicked on the excel button")
        a = QFileDialog.getOpenFileName(self, "Open file", "c:\\","Excel files (*.xls)")
        self.excelPath = a[0]
        self.filenameLabel.setText(f"File : {self.excelPath}")
    def click_data(self):
        """
        Called when we click on the button to load data.
        It will use a custom class and open a new window to type the data in.
        """
        super().__init__()
        self.emptyData()
        print("Clicked on the data button")
        self.orderWindow = None
        self.orderWindow = orderWindow()
        self.orderWindow.show()

class orderWindow(QWidget):
    """
    Window to type the orders data manually
    The new window is a widget it will appear in a separate window since it has no parents
    """
    def __init__(self):
        """
        We initialize the components for our GUI.
        """
        super().__init__()
        self.setWindowTitle("Type order data")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Press enter to add a row\nMove with the arrows\nType the number in the second column\nType pause start on 2nd line, 3rd column (hh:mm)\nType pause duration on 2nd line, 4th column (hh:mm)\nPress ok when done"))
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.cptRow = 0
        self.tableWidget.insertRow(0)
        self.cptRow += 1
        self.tableWidget.setItem(0, 0, QTableWidgetItem("Order name"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem("Number of items"))
        self.tableWidget.setItem(0, 2, QTableWidgetItem("Start of the maintenance"))
        self.tableWidget.setItem(0, 3, QTableWidgetItem("Duration of the maintenance"))
        self.tableWidget.insertRow(self.cptRow)
        self.tableWidget.setItem(1, 0, QTableWidgetItem(f"lot {self.cptRow}"))
        self.cptRow += 1
        layout.addWidget(self.tableWidget)
        self.okBtn = QPushButton("OK")
        self.okBtn.clicked.connect(lambda: self.clickOk())
        layout.addWidget(self.okBtn)
        self.setLayout(layout)
        self.setMinimumHeight(600)
        self.setMinimumWidth(500)

    def keyPressEvent(self, event):  
        """
        We insert a new row everytime we click enter
        """      
        if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            self.tableWidget.insertRow(self.cptRow)
            self.tableWidget.setItem(self.cptRow, 0, QTableWidgetItem(f"lot {self.cptRow}"))
            self.cptRow += 1
    def clickOk(self):
        """
        When we click ok, we will save the data then close the window
        """
        global tab_orders, pauseDuration, pauseStart
        #We use global variables because we need the variables in another class
        tab_orders = []
        for i in range(1, self.cptRow):#We add the number of items for each order in a list
            try:
                tab_orders.append(int(str(self.tableWidget.item(i, 1).text())))
            except Exception as e:
                print(e)
        try:#We try to get the pause duration and start (converted in minutes)
            startMinutes = int(str(self.tableWidget.item(1, 2).text()).split(":")[1])
            startHours = int(str(self.tableWidget.item(1, 2).text()).split(":")[0])
            pauseStart = startMinutes + startHours * 60
            durationMinutes = int(str(self.tableWidget.item(1, 3).text()).split(":")[1])
            durationHours = int(str(self.tableWidget.item(1, 3).text()).split(":")[0])
            pauseDuration = durationMinutes + durationHours * 60
            
        except Exception as e:
            print(e)
        self.close()
      

class TableWidget(QWidget):
    """
    Class for the tabs for displaying our gantt. We will have two tabs (like in a web browser for example)
    to see the differents gantt.
    """  
    def __init__(self, parent):
        """
        We initialize our components for the GUI
        """
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Task view")
        self.tabs.addTab(self.tab2,"Machine view")
        
        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.photoLabel1 = QLabel()
        self.tab1.layout.addWidget(self.photoLabel1)
        self.durationLabel1 = QLabel()
        self.tab1.layout.addWidget(self.durationLabel1)
        self.tab1.setLayout(self.tab1.layout)

        #Second tab
        self.tab2.layout = QVBoxLayout(self)
        self.photoLabel2 = QLabel()
        self.tab2.layout.addWidget(self.photoLabel2)
        self.durationLabel2 = QLabel()
        self.tab2.layout.addWidget(self.durationLabel2)
        self.tab2.setLayout(self.tab2.layout)
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def showTask(self, filePath, totalDuration, n):
        """
        We can load an image to the widget (we specify the number of the tab with n)
        """
        pixmap = QPixmap(filePath)
        if n == 1:
            self.photoLabel1.setPixmap(pixmap)
            self.durationLabel1.setText(f"Total duration : {totalDuration} minutes")
        elif n == 2:
            self.photoLabel2.setPixmap(pixmap)
            self.durationLabel2.setText(f"Total duration : {totalDuration} minutes")

app = QApplication([])

a = Window()
app.exec()