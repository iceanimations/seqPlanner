'''
Created on Jan 10, 2017

@author: qurban.ali
'''
import sip
sip.setapi('QString', 2)
import sys
sys.path.append('D:/My/Tasks/workSpace')
sys.path.append('D:/My/Tasks/workSpace/utilities')
sys.path.append('R:/Python_Scripts/plugins/utilities')
sys.path.append('R:/Python_Scripts/plugins')
sys.path.append('R:/Pipe_Repo/Projects/TACTIC')
from src import ui
from PyQt4.QtGui import QApplication, QStyleFactory

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyle(QStyleFactory.create('plastique'))
    win = ui.SeqPlanner()
    win.show()
    sys.exit(app.exec_())