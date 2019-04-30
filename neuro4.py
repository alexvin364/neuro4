from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from time import sleep

IMG_FLAG = QImage("./images/flag.png")
IMG_MSG = QImage("./images/msg.png")
IMG_START = QImage("./images/button1.png")
IMG_RESET = QImage("./images/button2.png")
IMG_BLANK = QImage("./images/blank.png")
SIZE = 5
SIZE2 = SIZE*SIZE

class Pos(QWidget):
    clicked = pyqtSignal()

    def __init__(self, x, y, s, *args, **kwargs):
        super(Pos, self).__init__(*args, **kwargs)

        self.setFixedSize(QSize(16, 16))
        self.x = x
        self.y = y
        self.s = s
        self.is_flagged = False
        self.update()
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = event.rect()
        outer, inner = Qt.gray, Qt.lightGray

        p.fillRect(r, QBrush(inner))
        pen = QPen(outer)
        pen.setWidth(1)
        p.setPen(pen)
        p.drawRect(r)
        
        if (self.s == "result"):
            if (result[(self.x-SIZE*2-SIZE//3)*SIZE+(self.y-SIZE-3)]==1):
                self.is_flagged = True
            else:
                self.is_flagged = False
        if self.is_flagged:
            p.drawPixmap(r, QPixmap(IMG_FLAG))
        self.update()

            
    def flag(self):
        s = self.s
        if self.is_flagged:
            self.is_flagged = False
            if (s == "l1"):
                first_learn[self.x*SIZE+self.y]=-1
            elif (s == "l2"):
                second_learn[(self.x-3-SIZE)*SIZE+self.y]=-1
            elif (s == "l3"):
                third_learn[(self.x-6-SIZE*2)*SIZE+self.y]=-1
            elif (s == "sample"):
                sample[(self.x-SIZE//3)*SIZE+(self.y-SIZE-3)]=-1
            elif (s == "result"):
                result[(self.x-SIZE*2-SIZE//3)*SIZE+(self.y-SIZE-3)]=-1
        else:
            self.is_flagged = True
            if (s == "l1"):
                first_learn[self.x*SIZE+self.y]=1
            elif (s == "l2"):
                second_learn[(self.x-3-SIZE)*SIZE+self.y]=1
            elif (s == "l3"):
                third_learn[(self.x-6-SIZE*2)*SIZE+self.y]=1
            elif (s == "sample"):
                sample[(self.x-SIZE//3)*SIZE+(self.y-SIZE-3)]=1
            elif (s == "result"):
                result[(self.x-SIZE*2-SIZE//3)*SIZE+(self.y-SIZE-3)]=1

        self.update()

        self.clicked.emit()

    def reveal(self):
        self.is_revealed = True
        self.update()


    def mouseReleaseEvent(self, e):
        if (e.button() == Qt.RightButton):
            self.flag()

        elif (e.button() == Qt.LeftButton):
            self.flag()


class Fake(QWidget):
    clicked = pyqtSignal()

    def __init__(self, x, y, *args, **kwargs):
        super(Fake, self).__init__(*args, **kwargs)
        self.setFixedSize(QSize(16, 16))
        self.x = x
        self.y = y
        self.update()
        
    def paintEvent(self, event):
        p = QPainter(self)
        r = event.rect()
        p.drawPixmap(r, QPixmap(IMG_BLANK))
            
    def reveal(self):
        self.is_revealed = True
        self.update()


class Button(QWidget):
    clicked = pyqtSignal()
    
    def __init__(self, x, y, *args, **kwargs):
        super(Button, self).__init__(*args, **kwargs)
        self.setFixedSize(QSize(80, 16))
        self.x = x
        self.y = y
        self.is_flagged = True
        self.update()
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = event.rect()
        outer, inner = Qt.gray, Qt.lightGray

        p.fillRect(r, QBrush(inner))
        pen = QPen(outer)
        pen.setWidth(1)
        p.setPen(pen)
        p.drawRect(r)

        if self.is_flagged:
            p.drawPixmap(r, QPixmap(IMG_START))
        else:
            p.drawPixmap(r, QPixmap(IMG_RESET))
            
    def flag(self):
        if self.is_flagged:
            Hopfield()
            for x in range(SIZE*2+SIZE//3, SIZE*3+SIZE//3):
                for y in range(SIZE+3, SIZE*2+3):
                    Pos(x, y, "result").reveal()
            self.is_flagged = False
        else:
            Reset()
            for x in range(SIZE*2+SIZE//3, SIZE*3+SIZE//3):
                for y in range(SIZE+3, SIZE*2+3):
                    Pos(x, y, "result").reveal()
            self.is_flagged = True
        self.update()
        self.clicked.emit()

    def reveal(self):
        self.is_revealed = True
        self.update()

    def mouseReleaseEvent(self, e):
        if (e.button() == Qt.LeftButton):
            self.flag()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.b_size = SIZE

        w = QWidget()
        hb = QHBoxLayout()
        
        self.button = QPushButton()
        self.button.setFixedSize(QSize(5, 5))
        self.button.setIconSize(QSize(5, 5))
        self.button.setFlat(True)

        hb.addWidget(self.button)
        
        l = QLabel()
        l.setPixmap(QPixmap.fromImage(IMG_MSG))
        l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        hb.addWidget(l)

        vb = QVBoxLayout()
        vb.addLayout(hb)

        self.grid = QGridLayout()
        self.grid.setSpacing(5)

        vb.addLayout(self.grid)
        w.setLayout(vb)
        self.setCentralWidget(w)

        self.init_map()
        self.show()

    def init_map(self):
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = Pos(x, y, "l1")
                self.grid.addWidget(w, y, x)
        for x in range(self.b_size, self.b_size+3):
            for y in range(0, self.b_size):
                w = Fake(x, y)
                self.grid.addWidget(w, y, x)
                
        for x in range(self.b_size+3, self.b_size*2+3):
            for y in range(0, self.b_size):
                w = Pos(x, y, "l2")
                self.grid.addWidget(w, y, x)
        for x in range(self.b_size*2+3, self.b_size*2+6):
            for y in range(0, self.b_size):
                w = Fake(x, y)
                self.grid.addWidget(w, y, x)
                
        for x in range(self.b_size*2+6, self.b_size*3+6):
            for y in range(0, self.b_size):
                w = Pos(x, y, "l3")
                self.grid.addWidget(w, y, x)
        for x in range(0, self.b_size*3+self.b_size//3):
            for y in range(self.b_size, self.b_size+3):
                w = Fake(x, y)
                self.grid.addWidget(w, y, x)       
                
        for x in range(0, self.b_size//3):
            for y in range(self.b_size, self.b_size*2):
                w = Fake(x, y)
                self.grid.addWidget(w, y, x)        
        for x in range(self.b_size//3, self.b_size+self.b_size//3):
            for y in range(self.b_size+3, self.b_size*2+3):
                w = Pos(x, y, "sample")
                self.grid.addWidget(w, y, x)
                
        for x in range(self.b_size+self.b_size//3, self.b_size*2+self.b_size//3):
            for y in range(self.b_size+3, self.b_size*2+3):
                w = Fake(x, y)
                self.grid.addWidget(w, y, x)
        for x in range(self.b_size*2+self.b_size//3, self.b_size*3+self.b_size//3):
            for y in range(self.b_size+3, self.b_size*2+3):
                w = Pos(x, y, "result")
                self.grid.addWidget(w, y, x)
        for x in range(self.b_size*3+self.b_size//3, self.b_size*4-self.b_size//3):
            for y in range(self.b_size+3, self.b_size*2+3):
                w = Fake(x, y)
                self.grid.addWidget(w, y, x)
        x = self.b_size*4+2-self.b_size//3
        y = self.b_size+3+self.b_size//2
        w = Button(x,y)
        self.grid.addWidget(w,y,x)
        for x in range(self.b_size*4+3-self.b_size//3, self.b_size*4):
            for y in range(self.b_size+3, self.b_size*2+3):
                w = Fake(x, y)
                self.grid.addWidget(w, y, x)

def f_net(net, prev):
    if (net>0): return 1
    elif (net<0): return -1
    else: return prev
    
def eq_check(x,y):
    for i in x:
        if x[i]!=y[i]:
            return 0
    return 1
    
def Hopfield():
    
    y = [sample[i] for i in range(SIZE2)]
    y_prev = [0 for i in range(SIZE2)]

    for k in range(SIZE2):
        for j in range(SIZE2):
            if (k!=j):
                weights[j][k]+=first_learn[k]*first_learn[j]
                weights[j][k]+=second_learn[k]*second_learn[j]
                weights[j][k]+=third_learn[k]*third_learn[j]
    c = 0
    while not eq_check(y, y_prev):
        #print(y)
        net = [0 for i in range(SIZE2)]
        for i in range(SIZE2):
            y_prev[i] = y[i]
        for k in range(SIZE2):
            for j in range(SIZE2):
                net[k]+=weights[j][k]*y_prev[j]
            net[k] = f_net(net[k],y_prev[k])
        for i in range(SIZE2):
            y[i] = net[i]
        c+=1
    #print(c)
    for i in range(SIZE2):
        result[i] = y[i]
        
    
def Reset():
    for i in range(SIZE2):
        result[i] = -1
    

if __name__ == '__main__':
    first_learn=[-1 for i in range(SIZE2)]
    second_learn=[-1 for i in range(SIZE2)]
    third_learn=[-1 for i in range(SIZE2)]
    weights = [[0 for i in range(SIZE2)] for j in range(SIZE2)]
    sample=[-1 for i in range(SIZE2)]
    result=[-1 for i in range(SIZE2)]
    app = QApplication([])
    window = MainWindow()
    app.exec_()

    