# -*- coding: utf-8 -*-

import os
from pprint import pprint, pformat
from datetime import datetime

from PySide import QtCore, QtGui

import pymongo, gridfs
from bson.objectid import ObjectId

#from jhighlighter import *

# ssh root@77.244.215.168 -Nf -L 27018:localhost:27017
client = pymongo.MongoClient("mongodb://localhost:27018/")
db = client["МиКМ2"]
#db.authenticate("bya965", "LabMMPiSSU303")
fs = gridfs.GridFS(db)
students = db["Студенты"]

years = (\
  '2020',\
  '2019',\
  '2018',\
  '2017',\
  '2016',\
  '2015',\
  '2014',\
  '2013',\
)

teachers = (\
  "Блинков Ю.А.",\
  #"Иванов В.А.",\
  "Иванов С.В.",\
  "Кальянов Л.В.",\
  "Кожанов В.С.",\
  "Кондратов Д.В.",\
  "Крылова Е.Ю.",\
  "Кузнецова О.С.",\
  "Мельникова Ю.В.",\
  #"Орел А.А.",\
  "Панкратов И.А.",\
  "Плаксина И.В.",\
  #"Ромакина О.М.",\
  "Шевырев С.П.",\
)

groups = set()
for y in years:
  groups = groups.union(students.aggregate([
    {'$group': {'_id': None,
      'группа': {'$addToSet': "$год.%s.группа" % y}}}]).next()["группа"])
#pprint(groups)

class Wizard(QtGui.QWizard):
  def __init__(self, parent=None):
    super(Wizard, self).__init__(parent)

    self.setWindowTitle('Студенты')
    self.student = None
    self.year = None

    self.addPage(ChooseStudent(self))
    self.addPage(StudentYear(self))

    self.currentIdChanged.connect(self.update)

    self.resize(QtCore.QSize(900, 600))

  def update(self, _id):
    if _id >= 0:
      self.page(_id).update()


class ChooseStudent(QtGui.QWizardPage):
  def __init__(self, parent=None):
    super(ChooseStudent, self).__init__(parent)

    class Model(QtCore.QAbstractTableModel):
      header = (\
        '_id',\
        'ФИО',\
        'email',\
        'год',\
        'группа',\
        'руководитель',\
      )

      def __init__(self, parent=None):
        super(Model, self).__init__(parent)
        self.lst = []

      def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and\
            role == QtCore.Qt.DisplayRole):
          return self.header[column]

      def rowCount(self, parent=None): return len(self.lst)
      def columnCount(self, parent=None): return len(self.header)

      def data(self, index, role):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
          return self.lst[index.row()][index.column()]

      def sort(self, column, order):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.lst.sort(key=lambda row: row[column], reverse=order == QtCore.Qt.AscendingOrder)
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    self.model = Model()
    self.table = QtGui.QTableView()
    self.table.setModel(self.model)
    self.table.setSelectionMode(QtGui.QTableView.SingleSelection)
    self.table.setAlternatingRowColors(True)
    self.table.setSelectionBehavior(QtGui.QTableView.SelectRows)
    self.table.setSortingEnabled(True)
    selectionModel = self.table.selectionModel() # TODO
    selectionModel.currentChanged.connect(self.currentChanged)
    self.table.setColumnHidden(0, True)

    self.findButton = QtGui.QPushButton("Найти")
    self.findButton.clicked.connect(self.find)

    self.editButton = QtGui.QPushButton("Править")
    self.editButton.clicked.connect(self.edit)

    self.copyButton = QtGui.QPushButton("Копировать запрос")
    self.copyButton.clicked.connect(self.copy)

    buttonsLayout = QtGui.QHBoxLayout()

    buttonsLayout.addWidget(QtGui.QLabel("ФИО:"))
    self.fio = QtGui.QLineEdit()

    buttonsLayout.addWidget(self.fio)
    buttonsLayout.addWidget(QtGui.QLabel("email:"))
    self.email = QtGui.QLineEdit()
    buttonsLayout.addWidget(self.email)

    self.year = QtGui.QComboBox()
    self.year.addItem("год")
    self.year.addItems(years)
    buttonsLayout.addWidget(self.year)

    self.group = QtGui.QComboBox()
    self.group.addItem("группа")
    #pprint(list(groups))
    self.group.addItems(sorted(groups))
    buttonsLayout.addWidget(self.group)

    self.teacher = QtGui.QComboBox()
    self.teacher.addItem("руководитель")
    self.teacher.addItems(teachers)
    buttonsLayout.addWidget(self.teacher)

    buttonsLayout.addStretch(1)
    buttonsLayout.addWidget(self.findButton)
    buttonsLayout.addWidget(self.editButton)
    buttonsLayout.addWidget(self.copyButton)

    layout = QtGui.QVBoxLayout()
    layout.addLayout(buttonsLayout, 1)
    layout.addWidget(self.table)
    self.setLayout(layout)

  def update(self):
    wizard.button(QtGui.QWizard.NextButton).setEnabled(False)
    self.editButton.setEnabled(False)
    self.findButton.setDefault(True)

  def currentChanged(self, current, previous):
    wizard.button(QtGui.QWizard.NextButton).setEnabled(current.isValid())
    self.editButton.setEnabled(current.isValid())
    if current.isValid():
      r = current.row()
      wizard.student = self.model.lst[r][0]
      wizard.year = self.model.lst[r][3]

  def filter(self):
    f = {}
    if self.fio.text():
      f['ФИО'] = {'$regex': self.fio.text(), '$options': 'i'}
    if self.email.text():
      f['email'] = {'$regex': self.email.text(), '$options': 'i'}
    if self.year.currentIndex() > 0 and \
       self.group.currentIndex() == 0 and \
       self.teacher.currentIndex() == 0:
      f['год.%s' % self.year.currentText()] = {'$exists': 1}
    group = []
    if self.group.currentIndex() > 0:
      if self.year.currentIndex() > 0:
        group.append({'год.%s.группа' % self.year.currentText(): self.group.currentText()})
      else:
        for y in years:
          group.append({'год.%s.группа' % y: self.group.currentText()})
    teacher = []
    if self.teacher.currentIndex() > 0:
      if self.year.currentIndex() > 0:
        teacher.append({'год.%s.руководитель' % self.year.currentText(): self.teacher.currentText()})
      else:
        for y in years:
          teacher.append({'год.%s.руководитель' % y: self.teacher.currentText()})
    if group and teacher:
      f['$and'] = [{'$or': group}, {'$or': teacher}]
    elif group:
      f['$or'] = group
    elif teacher:
      f['$or'] = teacher
    return f

  def find(self):
    self.model.lst = []
    for s in students.find(self.filter()):
      for k, v in s['год'].items():
        self.model.lst.append((s['_id'], s['ФИО'], s.get('email', ''),\
            k, v['группа'], v.get('руководитель', '')))
    self.model.reset()
    self.table.resizeColumnsToContents()
    self.update()

  def edit(self):
    assert wizard.student
    self.model.reset()
    self.table.resizeColumnsToContents()

  def copy(self):
    clipboard = QtGui.QApplication.clipboard()
    clipboard.setText("""db.getCollection('Студенты').find(
%s
).sort({'ФИО': 1})""" % pformat(self.filter()))

class StudentYear(QtGui.QWizardPage):
  label = """<table border=0 cellspacing=2 cellpadding=3>
  <tr>
    <td align=right>ФИО:</td>
    <td align=left><b>%s</b></td>
  </tr>
  <tr>
    <td align=right>email:</td>
    <td align=left><b>%s</b></td>
  </tr>
  <tr>
    <td align=right>год:</td>
    <td align=left><b>%s</b></td>
  </tr>
  <tr>
    <td align=right>группа:</td>
    <td align=left><b>%s</b></td>
  </tr>
</table><br>"""

  def __init__(self, parent=None):
    super(StudentYear, self).__init__(parent)

    self.head = QtGui.QLabel()

    self.tema = QtGui.QPlainTextEdit()
    self.tema.modificationChanged.connect(self.updateTema)

    self.teacher = QtGui.QComboBox()
    self.teacher.addItem("")
    self.teacher.addItems(teachers)
    self.teacher.currentIndexChanged.connect(self.updateTeacher)

    self.reviewer = QtGui.QLineEdit()
    self.reviewer.textChanged.connect(self.updateReviewer)

    self.practice = QtGui.QCheckBox("практика")
    self.practice.clicked.connect(self.updatePractice)

    self.working = QtGui.QCheckBox("работа")
    self.working.clicked.connect(self.updateWorking)

    self.abstract = QtGui.QCheckBox("реферат")
    self.abstract.clicked.connect(self.updateAbstract)

    self.project = QtGui.QCheckBox("план")
    self.project.clicked.connect(self.updateProject)

    self.saveButton = QtGui.QPushButton("Сохранить")
    self.saveButton.clicked.connect(self.save)

    formLayout = QtGui.QFormLayout()
    formLayout.addRow("тема", self.tema)
    formLayout.addRow("руководитель", self.teacher)
    formLayout.addRow("рецензент", self.reviewer)
    formLayout.addRow("", self.practice)
    formLayout.addRow("", self.working)
    formLayout.addRow("", self.abstract)
    formLayout.addRow("", self.project)

    layout = QtGui.QVBoxLayout()
    layout.addWidget(self.head)
    layout.addLayout(formLayout, 1)
    buttonsLayout = QtGui.QHBoxLayout()
    buttonsLayout.addStretch(1)
    buttonsLayout.addWidget(self.saveButton)
    layout.addLayout(buttonsLayout, 1)
    self.setLayout(layout)

  def initializePage(self):
    finishText = wizard.buttonText(QtGui.QWizard.FinishButton)

  def update(self):
    #pprint(wizard.student)
    s = students.find_one({'_id': wizard.student})
    y = s['год'][wizard.year]
    self.head.setText(self.label % (s['ФИО'], s.get('email', ''), wizard.year, y['группа']))

    self.tema.setPlainText(y.get('тема', ''))
    self.teacher.setCurrentIndex(0)
    if "руководитель" in y:
      for i in range(self.teacher.count()):
        if self.teacher.itemText(i) == y["руководитель"]:
          self.teacher.setCurrentIndex(i)
          break
    self.reviewer.setText(y.get('рецензент', ''))

    self.practice.setChecked("практика" in y)
    self.working.setChecked("работа" in y)
    self.abstract.setChecked("реферат" in y)
    self.project.setChecked("план" in y)

    self.practiceFile = None
    self.workingFile = None
    self.abstractFile = None
    self.projectFile = None

    self.saveButton.setDefault(True)
    self.saveButton.setEnabled(False)

  def save(self):
    self.saveButton.setEnabled(False)
    s = students.find_one({'_id': wizard.student})
    y = s['год'][wizard.year]

    if self.tema.toPlainText():
      students.update_one({'_id': s['_id']},
        {'$set': {'год.%s.тема' %  wizard.year: self.tema.toPlainText()}},
        upsert=True)
    else:
      students.update_one({'_id': s['_id']},
        {'$unset': {'год.%s.тема' %  wizard.year: 1}})

    if self.teacher.currentText():
      students.update_one({'_id': s['_id']},
        {'$set': {'год.%s.руководитель' %  wizard.year: self.teacher.currentText()}},
        upsert=True)
    else:
      students.update_one({'_id': s['_id']},
        {'$unset': {'год.%s.руководитель' %  wizard.year: 1}})

    if self.reviewer.text():
      students.update_one({'_id': s['_id']},
        {'$set': {'год.%s.рецензент' %  wizard.year: self.reviewer.text()}},
        upsert=True)
    else:
      students.update_one({'_id': s['_id']},
        {'$unset': {'год.%s.рецензент' %  wizard.year: 1}})

    if self.practice.checkState() == QtCore.Qt.Unchecked:
      if "практика" in y:
        fs.delete(y["практика"])
        students.update_one({'_id': s['_id']},
          {'$unset': {'год.%s.практика' %  wizard.year: 1}})
    elif self.practiceFile:
      if "практика" in y:
        fs.delete(y["практика"])
      f_id = fs.put(open(self.practiceFile, 'rb'), filename=os.path.split(self.practiceFile)[1])
      #print(f_id, os.path.split(self.practiceFile)[1])
      students.update_one({'_id': s['_id']},
        {'$set': {'год.%s.практика' %  wizard.year: f_id}},
        upsert=True)

    if self.working.checkState() == QtCore.Qt.Unchecked:
      if "работа" in y:
        fs.delete(y["работа"])
        students.update_one({'_id': s['_id']},
          {'$unset': {'год.%s.работа' %  wizard.year: 1}})
    elif self.workingFile:
      if "работа" in y:
        fs.delete(y["работа"])
      f_id = fs.put(open(self.workingFile, 'rb'), filename=os.path.split(self.workingFile)[1])
      #print(f_id, os.path.split(self.workingFile)[1])
      students.update_one({'_id': s['_id']},
        {'$set': {'год.%s.работа' %  wizard.year: f_id}},
        upsert=True)

    if self.abstract.checkState() == QtCore.Qt.Unchecked:
      if "реферат" in y:
        fs.delete(y["реферат"])
        students.update_one({'_id': s['_id']},
          {'$unset': {'год.%s.реферат' %  wizard.year: 1}})
    elif self.abstractFile:
      if "реферат" in y:
        fs.delete(y["реферат"])
      f_id = fs.put(open(self.abstractFile, 'rb'), filename=os.path.split(self.abstractFile)[1])
      #print(f_id, os.path.split(self.abstractFile)[1])
      students.update_one({'_id': s['_id']},
        {'$set': {'год.%s.реферат' %  wizard.year: f_id}},
        upsert=True)

    if self.project.checkState() == QtCore.Qt.Unchecked:
      if "план" in y:
        fs.delete(y["план"])
        students.update_one({'_id': s['_id']},
          {'$unset': {'год.%s.план' %  wizard.year: 1}})
    elif self.projectFile:
      if "план" in y:
        fs.delete(y["план"])
      f_id = fs.put(open(self.projectFile, 'rb'), filename=os.path.split(self.projectFile)[1])
      #print(f_id, os.path.split(self.projectFile)[1])
      students.update_one({'_id': s['_id']},
        {'$set': {'год.%s.план' %  wizard.year: f_id}},
        upsert=True)

    self.practiceFile = None
    self.workingFile = None
    self.abstractFile = None
    self.projectFile = None

  def updateTema(self, changed):
    self.saveButton.setEnabled(True)

  def updateTeacher(self, index):
    self.saveButton.setEnabled(True)

  def updateReviewer(self, index):
    self.saveButton.setEnabled(True)

  def updatePractice(self):
    if self.practice.checkState() == QtCore.Qt.Unchecked:
      self.practiceFile = None
    else:
      editor = QtGui.QFileDialog(wizard, 'Загрузить отчет по практике')
      editor.setNameFilter("Документы (*.odt *.doc *.docx *.pdf)");
      editor.move(wizard.pos() + QtCore.QPoint(300, 100))
      editor.resize(QtCore.QSize(600, 800))
      if editor.exec_():
        self.practiceFile = editor.selectedFiles()[0]
      else:
        self.practiceFile = None
        self.practice.setChecked(False)

    self.saveButton.setEnabled(True)

  def updateWorking(self):
    if self.working.checkState() == QtCore.Qt.Unchecked:
      self.workingFile = None
    else:
      editor = QtGui.QFileDialog(wizard, 'Загрузить студентческую работу')
      editor.setNameFilter("Документы (*.odt *.doc *.docx *.pdf)");
      editor.move(wizard.pos() + QtCore.QPoint(300, 100))
      editor.resize(QtCore.QSize(600, 800))
      if editor.exec_():
        self.workingFile = editor.selectedFiles()[0]
      else:
        self.workingFile = None
        self.working.setChecked(False)

    self.saveButton.setEnabled(True)

  def updateAbstract(self):
    if self.abstract.checkState() == QtCore.Qt.Unchecked:
      self.abstractFile = None
    else:
      editor = QtGui.QFileDialog(wizard, 'Загрузить автореферат')
      editor.setNameFilter("Документы (*.odt *.doc *.docx *.pdf)");
      editor.move(wizard.pos() + QtCore.QPoint(300, 100))
      editor.resize(QtCore.QSize(600, 800))
      if editor.exec_():
        self.abstractFile = editor.selectedFiles()[0]
      else:
        self.abstractFile = None
        self.abstract.setChecked(False)

    self.saveButton.setEnabled(True)

  def updateProject(self):
    if self.project.checkState() == QtCore.Qt.Unchecked:
      self.projectFile = None
    else:
      editor = QtGui.QFileDialog(wizard, 'Загрузить индивидуальный план')
      editor.setNameFilter("Документы (*.odt *.doc *.docx *.pdf)");
      editor.move(wizard.pos() + QtCore.QPoint(300, 100))
      editor.resize(QtCore.QSize(600, 800))
      if editor.exec_():
        self.projectFile = editor.selectedFiles()[0]
      else:
        self.projectFile = None
        self.project.setChecked(False)

    self.saveButton.setEnabled(True)

if __name__ == '__main__':
  import sys

  app = QtGui.QApplication(sys.argv)
  QtCore.QLocale.setDefault(QtCore.QLocale("ru_RU"))

  translator = QtCore.QTranslator()
  translator.load('/usr/share/qt4/translations/qt_ru.qm')
  app.installTranslator(translator)

  font = QtGui.QApplication.font()
  font.setPointSize(font.pointSize() - 1)
  QtGui.QApplication.setFont(font)

  global wizard
  wizard = Wizard()
  wizard.show()
  sys.exit(app.exec_())
