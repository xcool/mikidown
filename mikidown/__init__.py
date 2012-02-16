#!/usr/bin/env python

import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from mikidown.config import *

__version__ = "0.0.1"

class MikiMenu(QMenuBar):
	def __init__(self, parent=None):
		super(MikiMenu, self).__init__(parent)
		self.menuFile = self.addMenu(self.tr('File'))
		self.menuEdit = self.addMenu('Edit')
		self.menuHelp = self.addMenu('Help')
		#self.menuFile.addAction(self.actionNew)
		#self.menuFile.addAction(self.actionOpen)
		self.menuExport = self.menuFile.addMenu('Export')

class RecentChanged(QListWidget):
	def __init__(self, parent=None):
		super(RecentChanged, self).__init__(parent)

class RecentViewed(QDialogButtonBox):
	def __init__(self, parent=None):
		super(RecentViewed, self).__init__(Qt.Horizontal, parent)
		sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		sizePolicy.setVerticalPolicy(QSizePolicy.Fixed)
		self.setSizePolicy(sizePolicy)

		self.addButton('old', QDialogButtonBox.ActionRole)
		self.addButton('new', QDialogButtonBox.ActionRole)
	
	def sizeHint(self):
		return QSize(400, 8)

class MikiTree(QTreeWidget):
	def __init__(self, parent=None):
		super(MikiTree, self).__init__(parent)
		self.header().close()
		self.setContextMenuPolicy(Qt.CustomContextMenu)
	def mousePressEvent(self, event):
		self.clearSelection()
		super(MikiTree, self).mousePressEvent(event)

class ItemDialog(QDialog):
	def __init__(self, parent=None):

		super(ItemDialog, self).__init__(parent)
		self.editor = QLineEdit()
		editorLabel = QLabel("Page Name:")
		editorLabel.setBuddy(self.editor)
		self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
										  QDialogButtonBox.Cancel)
		self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
		layout = QGridLayout()
		layout.addWidget(editorLabel, 0, 0)
		layout.addWidget(self.editor, 0, 1)
		layout.addWidget(self.buttonBox, 1, 1)
		self.setLayout(layout)
		self.connect(self.editor, SIGNAL("textEdited(QString)"),
					 self.updateUi)
		self.connect(self.buttonBox, SIGNAL("accepted()"), self.accept)
		self.connect(self.buttonBox, SIGNAL("rejected()"), self.reject)
	def updateUi(self):
		self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
				self.editor.text()!="")

class MikiWindow(QMainWindow):
	def __init__(self, notebookDir=None, parent=None):
		super(MikiWindow, self).__init__(parent)
		self.resize(800,600)
		screen = QDesktopWidget().screenGeometry()
		size = self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
		self.menubar = MikiMenu()
		self.setMenuBar(self.menubar)

		self.tabWidget = QTabWidget()
		self.viewedList = RecentViewed()
		self.notesEdit = QTextEdit()
		self.noteSplitter = QSplitter(Qt.Horizontal)
		self.noteSplitter.addWidget(self.notesEdit)
		self.rightSplitter = QSplitter(Qt.Vertical)
		self.rightSplitter.addWidget(self.viewedList)
		self.rightSplitter.addWidget(self.noteSplitter)
		self.mainSplitter = QSplitter(Qt.Horizontal)
		self.mainSplitter.addWidget(self.tabWidget)
		self.mainSplitter.addWidget(self.rightSplitter)
		self.setCentralWidget(self.mainSplitter)
		
		self.mainSplitter.setStretchFactor(0, 1)
		self.mainSplitter.setStretchFactor(1, 5)
		sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		sizePolicy.setVerticalPolicy(QSizePolicy.Fixed)
		self.viewedList.setSizePolicy(sizePolicy)

		self.notesTree = MikiTree()
		self.changedList = RecentChanged()
		self.tabWidget.addTab(self.notesTree, 'Index')
		self.tabWidget.addTab(self.changedList, 'Recently Changed')
		print(self.mainSplitter.sizes())
		print(self.rightSplitter.sizes())
		#self.rightSplitter.setSizes([600,20,600,580])
		self.rightSplitter.setStretchFactor(0, 0)

		
		self.previewBox = QTextEdit()
		self.connect(self.notesTree, SIGNAL('customContextMenuRequested(QPoint)'),
				     self.treeMenu)
		self.connect(self.notesTree, SIGNAL('itemClicked(QTreeWidgetItem *,int)'),
				self.showNote)
		self.connect(self.notesTree, 
					 SIGNAL('currentItemChanged(QTreeWidgetItem*, QTreeWidgetItem*)'),
					 self.saveNote)
		self.connect(self.notesEdit,
					 SIGNAL('textChanged()'),
					 self.noteEditted)

		QDir.setCurrent(notebookDir)
		self.mikiDir = QDir(notebookDir)
		self.mikiDir = QDir.current()
		#self.initTree(self.mikiDir, self.notesTree)	
		self.editted = 0
		self.initTree(notebookDir, self.notesTree)
	def initTree(self, notePath, parent):
		#self.notesList = self.mikiDir.entryList(["*.markdown"],
		#if noteDir is None:
		#	return
		if not QDir(notePath).exists():
			return
		noteDir = QDir(notePath)
		#noteDir.setCurrent(notePath)
		self.notesList = noteDir.entryList(["*.markdown"],
							   QDir.NoFilter,
							   QDir.Name)

		for note in self.notesList:
			fi = QFileInfo(note)
			item = QTreeWidgetItem(parent, [fi.baseName()])
			#item = QTreeWidgetItem(self.notesTree, [fi.baseName()])
			#path = noteDir.currentPath() + '/' + fi.baseName()
			path = self.tr(notePath + '/' + fi.baseName())
			print(path)
			#aDir = QDir(path)
			#aDir.setCurrent(path)
			#print(aDir.currentPath())
			self.initTree(path, item)
			#self.initIterator(
	#def initIterator(self, path, parent):
	def getPath(self, item):
		item = item.parent()
		path = ''
		while item is not None:
			path = item.text(0) + '/' + path
			item = item.parent()
		return path
	def saveNote(self, current, previous):
		#self.filename = self.notebookDir + previous.text(0) + '.markdown'
		if previous is None:
			return
		if self.editted == 0:
			return
		self.editted = 1
		self.filename = previous.text(0)+".markdown"
		self.path = self.getPath(previous)
		print(self.path)
		fh = QFile(self.path + self.filename)
		try:
			if not fh.open(QIODevice.WriteOnly):
				raise IOError(fh.errorString())
		except IOError as e:
			QMessageBox.warning(self, "Save Error",
						"Failed to save %s: %s" % (self.filename, e))
		finally:
			if fh is not None:
				savestream = QTextStream(fh)
				savestream << self.notesEdit.toPlainText()
				fh.close()
				#QTextStream(fh).writeAll()
				#fh.writeData(self.notesEdit)
	def noteEditted(self):
		self.editted = 1
	def treeMenu(self):
		menu = QMenu()
		#for text in ("a", "b", "c"):
		#	action = menu.addAction(text)
		menu.addAction("New Page", self.newPage)
		menu.addAction("New Subpage", self.newSubpage)
		self.delCallback = lambda item=self.notesTree.currentItem(): self.delPage(item)
		menu.addAction("Delete Page", self.delCallback)
		#menu.addAction("Delete Page", self.delPage(self.notesTree.currentItem()))
		menu.addAction("Collapse All", self.collapseAll)
		menu.addAction("Uncollapse All", self.uncollapseAll)
		menu.addAction("a", self.hello)
		menu.exec_(QCursor.pos())
	
	def newPage(self):
		dialog = ItemDialog(self)
		if dialog.exec_():
			self.filename = dialog.editor.text()
			#QDir.current().mkdir(self.filename)
			fh = QFile(self.filename+'.markdown')
			try:
				if not fh.open(QIODevice.WriteOnly):
					raise IOError(fh.errorString())
			except IOError as e:
				QMessageBox.warning(self, "Create Error",
						"Failed to create %s: %s" % (self.filename, e))
			finally:
				if fh is not None:
					fh.close()
			QTreeWidgetItem(self.notesTree, [self.filename])
			self.notesTree.sortItems(0, Qt.AscendingOrder)
		self.editted = 0
	#def newSubpage(self, selectedPage=None, col=None):
	def newSubpage(self):
		dialog = ItemDialog(self)
		if dialog.exec_():
			#self.filename = QDir.currentPath()+'/'+self.notesTree.currentItem().text(0)+'/'+dialog.editor.text()
			self.filename = dialog.editor.text()
			self.path = self.notesTree.currentItem().text(0) + '/'
			item = self.notesTree.currentItem().parent()
			while item is not None:
				self.path = item.text(0) + '/' + self.path
				item = item.parent()
			#self.filename = self.notesTree.currentItem().text(0) + '/'+dialog.editor.text()
			QDir.current().mkdir(self.path)
			print(self.path + self.filename)
			fh = QFile(self.path+self.filename+'.markdown')
			fh.open(QIODevice.WriteOnly)
			fh.close()
			QTreeWidgetItem(self.notesTree.currentItem(), [dialog.editor.text()])
			self.notesTree.sortItems(0, Qt.AscendingOrder)
			self.notesTree.expandItem(self.notesTree.currentItem())
			
		self.editted = 0
	def delPage(self, item):
		#self.notesTree.removeItemWidget(self.notesTree.currentItem(),0)
		#QTreeWidget.removeItemWidget(self.notesTree,
		#		self.notesTree.currentItem(),0)
		#self.notesTree.currentItem.delete()
		#path = self.getPath(item)
		childNum = item.childCount()
		#if childNum == 0:
		#	return
		#	path = self.getPath(item)
		#	QDir.current().remove(path + item.text(0) + '.markdown')
		#	parent = item.parent()
		#	if parent is not None:
		#		index = parent.indexOfChild(item)
		#		parent.takeChild(index)
		#	else:
		#		index = self.notesTree.indexOfTopLevelItem(item)
		#		self.notesTree.takeTopLevelItem(index)	
		if childNum > 0:
			for index in range(0, childNum):
				self.dirname = item.child(index).text(0)
				#path = self.getPath(item.child(index))
				self.delPage(item.child(index))
				#print(path + self.dirname)
				#QDir.current().rmdir(path + self.dirname)

		path = self.getPath(item)
		QDir.current().remove(path + item.text(0) + '.markdown')
		parent = item.parent()
		if parent is not None:
			index = parent.indexOfChild(item)
			parent.takeChild(index)
			if parent.childCount() == 0:
				QDir.current().rmdir(path)
		else:
			index = self.notesTree.indexOfTopLevelItem(item)
			self.notesTree.takeTopLevelItem(index)	
		print(path+item.text(0))
		QDir.current().rmdir(path + item.text(0))
		#print(item.text(0))
		#self.dirname = self.notesTree.currentItem().text(0)
		#QDir.current().rmdir(self.dirname)
		#QDir.current().remove(self.dirname+".markdown")
		#index = self.notesTree.indexOfTopLevelItem(self.notesTree.currentItem())
		#self.notesTree.takeTopLevelItem(index)
	def collapseAll(self):
		self.notesTree.collapseAll()
	def uncollapseAll(self):
		self.notesTree.expandAll()
	def showNote(self, note):
		#self.path = self.notesTree.currentItem().text(0) + '/'
		#item = self.notesTree.currentItem().parent()		
		#while item is not None:
		#	self.path = item.text(0) + '/' + self.path
		#	item = item.parent()
		self.path = self.getPath(self.notesTree.currentItem())
		self.notesEdit.setText(self.path)

		self.filename = note.text(0)+".markdown"
		#self.notesEdit.clear()
		#self.notesEdit.setText(note.text(0))
		fh = QFile(self.path + self.filename)
		try:
			if not fh.open(QIODevice.ReadWrite):
				raise IOError(fh.errorString())
		except IOError as e:
			QMessageBox.warning(self, "Read Error",
					"Failed to open %s: %s" % (self.filename, e))
		finally:
			if fh is not None:
				noteBody = QTextStream(fh).readAll()
				#noteBody = fh.readLink(self.filename)
				fh.close()
		#body = PyQt4.QtCore.QString(noteBody)
		#self.notesEdit.setPlainText(noteBody)
		self.notesEdit.insertPlainText(noteBody)
		self.editted = 0
	def hello(self):
		self.notesEdit.append("Hello")


def main():
	app = QApplication(sys.argv)
	XDG_CONFIG_HOME = os.environ['XDG_CONFIG_HOME']
	config_dir = XDG_CONFIG_HOME + '/mikidown/'
	config_file = config_dir + 'notebooks.list'
	print(config_file)
	if not os.path.isfile(config_file):
		NotebookList.create()
	fh = QFile(config_file)
	fh.open(QIODevice.ReadOnly)
	notebookInfo = QTextStream(fh).readAll()

	notebookDir = notebookInfo.split(' ')[1]
	print(notebookDir)
	#NotebookList.read()
	window = MikiWindow(notebookDir)
	window.show()
	#NotebookList.create()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
