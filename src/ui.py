'''
Created on Jul 2, 2015

@author: qurban.ali
'''
from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import cui
import os.path as osp
import appUsageApp
import tacticCalls as tc
import traceback
import iutil
import os

from pprint import pprint


reload(tc)
reload(cui)
reload(iutil)

root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')
icon_path = osp.join(root_path, 'icon')
__title__ = 'Sequence Planner'

Form, Base = uic.loadUiType(osp.join(ui_path, 'main.ui'))
class SeqPlanner(Form, Base, cui.TacticUiBase):
    def __init__(self, parent=None):
        super(SeqPlanner, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(__title__)
        #self.setStyleSheet(cui.styleSheet)
        self.setServer()
        
        self.flowLayout = cui.FlowLayout()
        self.flowLayout.setSpacing(2)
        self.mainLayout.insertLayout(0, self.flowLayout)
        
        self.projectBox = QComboBox(); self.projectBox.addItem('--Select Project--')
        self.epBox = QComboBox(); self.epBox.addItem('--Select Episode--')
        
        self.sequenceItems = []
        self.collapsed = True

        self.populateProjects()
        
        self.flowLayout.addWidget(self.projectBox)
        self.flowLayout.addWidget(self.epBox)

        self.projectBox.currentIndexChanged[str].connect(self.setProject)
        self.epBox.currentIndexChanged[str].connect(self.populateEpisodeAssets)
        self.toggleCollapseButton.clicked.connect(self.toggleItems)
        self.searchBox.textChanged.connect(self.searchItems)
        
        self.toggleCollapseButton.setIcon(QIcon(osp.join(icon_path, 'ic_toggle_collapse')))
        search_ic_path = osp.join(icon_path, 'ic_search.png').replace('\\','/')
        style_sheet = ('\nbackground-image: url(%s);'+
                       '\nbackground-repeat: no-repeat;'+
                       '\nbackground-position: center left;'+
                       '\npadding-left: 15px;\npadding-bottom: 1px;\n')%search_ic_path
        style_sheet = self.searchBox.styleSheet() + style_sheet
        self.searchBox.setStyleSheet(style_sheet)
        self.splitter_2.setSizes([(self.height() * 30) / 100, (self.height() * 50) / 100])
        
        appUsageApp.updateDatabase('sequencePlanner')
        
    def setBusy(self):
        qApp.setOverrideCursor(Qt.WaitCursor)
        qApp.processEvents()
        
    def releaseBusy(self):
        qApp.restoreOverrideCursor()
        qApp.processEvents()
        
    def toggleItems(self):
        self.collapsed = not self.collapsed
        for item in self.sequenceItems:
            item.toggleCollapse(self.collapsed)
    
    def getSelectedAssets(self):
        return [item.text() for item in self.assetBox.selectedItems()]
    
    def clearPlanner(self):
        for item in self.sequenceItems:
            item.deleteLater()
        del self.sequenceItems[:]
        
    def populateEpisodeAssets(self, ep):
        self.assetBox.clear()
        self.clearPlanner()
        if not ep or ep == '--Select Episode--': return
        self.setBusy()
        assets, errors = tc.getAssetsInEp(ep)
        if assets:
            
            self.assetBox.addItems(sorted(assets))
            errors.update(self.populateSequencePlanner(ep))
        if errors:
            self.showMessage(msg='Errors occurred while retrieving data from TACTIC',
                             details=iutil.dictionaryToDetails(errors),
                             icon=QMessageBox.Critical)
        self.releaseBusy()
        
    def populateSequencePlanner(self, ep):
        self.clearPlanner()
        if not ep or ep == '--Select Episode--': return
        errors = {}
        seqs, err = tc.getSequences(ep)
        if err:
            errors.update(err)
        for seq in seqs:
            assets = None
            assets, err = tc.assetsInSeq(seq)
            if err:
                errors.update(err)
            item = Item(self, title=seq, name=seq)
            self.sequenceItems.append(item)
            self.itemsLayout.addWidget(item)
            if assets:
                item.addItems(assets)
        return errors
        
    def showMessage(self, **kwargs):
        return cui.showMessage(self, __title__, **kwargs)
        
    def closeEvent(self, event):
        self.deleteLater()
    
    def searchItems(self, text=''):
        if not text:
            text = self.searchBox.text()
        if text:
            for item in self.sequenceItems:
                if text.lower() in item.getTitle().lower():
                    item.show()
                else: item.hide()
        else:
            for item in self.sequenceItems:
                item.show()
            
Form2, Base2 = uic.loadUiType(osp.join(ui_path, 'item.ui'))
class Item(Form2, Base2):
    def __init__(self, parent=None, title='', name=''):
        super(Item, self).__init__(parent)
        self.setupUi(self)
        self.parentWin = parent
        self.collapsed = False
        self.name = name
        if title: self.setTitle(title)
        self.style = ('background-image: url(%s);\n'+
                      'background-repeat: no-repeat;\n'+
                      'background-position: center right')

        if not self.userAllowed():
            self.removeButton.setEnabled(False);
            self.addButton.setEnabled(False)
        
        self.iconLabel.setStyleSheet(self.style%osp.join(icon_path,
                                                         'ic_collapse.png').replace('\\', '/'))
        self.removeButton.setIcon(QIcon(osp.join(icon_path, 'ic_remove_char.png')))
        self.addButton.setIcon(QIcon(osp.join(icon_path, 'ic_add_char.png')))

        self.titleFrame.mouseReleaseEvent = self.collapse
        self.addButton.clicked.connect(self.addSelectedItems)
        self.removeButton.clicked.connect(self.removeItems)
        
    def userAllowed(self):
        if iutil.getUsername() in ['qurban.ali', 'talha.ahmed',
                'mohammad.bilal', 'umair.shahid', 'sarmad.mushtaq',
                'fayyaz.ahmed',
                'muhammad.shareef', 'rafaiz.jilani', 'shahzaib.khan' ]:
            return True

    def collapse(self, event=None):
        if self.collapsed:
            self.listBox.show()
            self.collapsed = False
            path = osp.join(icon_path, 'ic_collapse.png')
        else:
            self.listBox.hide()
            self.collapsed = True
            path = osp.join(icon_path, 'ic_expand.png')
        path = path.replace('\\', '/')
        self.iconLabel.setStyleSheet(self.style%path)

    def toggleCollapse(self, state):
        self.collapsed = state
        self.collapse()

    def getTitle(self):
        return str(self.nameLabel.text())
    
    def setTitle(self, title):
        self.nameLabel.setText(title)
        
    def updateNum(self):
        self.numLabel.setText('('+ str(self.listBox.count()) +')')
        
    def addAssetsToTactic(self, assets):
        flag = False
        self.parentWin.setBusy()
        try:
            errors = tc.addAssetsToSeq(assets, self.name)
            if errors:
                self.parentWin.showMessage(msg='Error occurred while adding Assets to %s'%self.name,
                                           icon=QMessageBox.Critical,
                                           details=iutil.dictionaryToDetails(errors))
            else:
                flag = True
        except Exception as ex:
            self.parentWin.releaseBusy()
            self.parentWin.showMessage(msg=str(ex), icon=QMessageBox.Critical)
        finally:
            self.parentWin.releaseBusy()
        return flag
        
    def addItems(self, items):
        while self.listBox.count() > 0:
            items.append(self.listBox.takeItem(0).text())
        self.listBox.addItems(sorted(items))
        self.updateNum()
        
    def addSelectedItems(self):
        assets = self.parentWin.getSelectedAssets()
        if not assets: return
        if self.addAssetsToTactic(assets):
            self.addItems(assets)
    
    def removeItems(self):
        self.parentWin.setBusy()
        try:
            assets = self.listBox.selectedItems()
            if assets:
                errors = tc.removeAssetsFromSeq([item.text() for item in assets], self.name)
                if errors:
                    self.parentWin.showMessage(msg='Error occurred while Removing Assets from %s'%self.name,
                                               icon=QMessageBox.Critical,
                                               details=iutil.dictionaryToDetails(errors))
                    return
                for item in assets:
                    self.listBox.takeItem(self.listBox.row(item))
        except Exception as ex:
            self.parentWin.releaseBusy()
            self.parentWin.showMessage(msg=str(ex), icon=QMessageBox.Critical)
        finally:
            self.parentWin.releaseBusy()
        self.updateNum()
            
    def getItems(self):
        items = []
        for i in range(self.listBox.count()):
            items.append(self.listBox.item(i).text())
        return items