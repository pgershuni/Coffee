import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog,QMessageBox
from PyQt5.QtWidgets import QLineEdit,QDialogButtonBox,QFormLayout, QComboBox
from PyQt5.QtCore import Qt
from main_form import Ui_FrmMain
from addEditCoffeeForm import Ui_FormaddCoffee

class InputDialogOneField(QDialog):
    ValueNames = []

    def WinCaption(self, title):
        self.setWindowTitle(title)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.name = QLineEdit(self)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        layout = QFormLayout(self)
        layout.addRow("Название", self.name)
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def setValueNames(self, ArValues):
        self.ValueNames.clear()
        self.ValueNames = ArValues

    def accept(self):
        if self.name.text() == '':
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setWindowTitle("Ошибка")
            msgBox.setText("Название не заполнено")
            msgBox.exec()
            return
        if self.name.text() in self.ValueNames:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setWindowTitle("Ошибка")
            msgBox.setText("Такое название уже есть в справочнике")
            msgBox.exec()
            return
        super().accept()

    def getInputs(self):
        return (self.name.text())

    def setValues(self, param):
        self.name.setText(param)


class FrmEditCoffee(QMainWindow, Ui_FormaddCoffee):
    db_name = ''
    result = []
    FormArrayFrm = []
    RoastArrayFrm = []

    def __init__(self):
        super().__init__()
        #uic.loadUi('addEditCoffeeForm.ui', self)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setGeometry(0, 0, 450, 230)
        self.db_name = "DATA\coffee.sqlite"
        self.editPrice.setText("0")
        self.editValue.setText("0")
        self.BtnPressed  = 0
        self.BtnCancel.clicked.connect(self.btn_cancel)
        self.BtnOK.clicked.connect(self.btn_ok)

    def OnShow(self):
        self.GetSpravFrm(self.db_name)
        self.CBForm.clear()
        self.CBRoast.clear()
        self.CBRoast.addItems([a[0] for a in self.RoastArrayFrm])
        self.CBForm.addItems([a[0] for a in self.FormArrayFrm])
        self.BtnPressed = 0

    def GetSpravFrm(self, db_name):
        self.con = sqlite3.connect(self.db_name)
        cur = self.con.cursor()
        query = '''
            SELECT form_name, form_id
            from form    
            ORDER BY 1
            '''
        tmp = cur.execute(query).fetchall()
        for row in tmp:
            self.FormArrayFrm.append([row[0],row[1]])
        cur.close()

        query = '''
                    SELECT roast_name, roast_id
                    from roast    
                    ORDER BY 1
                    '''
        cur = self.con.cursor()
        tmp = cur.execute(query).fetchall()
        for row in tmp:
            self.RoastArrayFrm.append([row[0], row[1]])
        cur.close()

    def btn_cancel(self):
        self.BtnPressed = 0
        self.hide()

    def btn_ok(self):
        err= False
        if not self.isinteger(self.editPrice.text()):
            self.statusBar().showMessage('Цена должна быть целым числом')
            err = True
        if int(self.editPrice.text())<=0:
            self.statusBar().showMessage('Цена должна быть положительным числом')
            err = True
        if  not self.isinteger(self.editValue.text()):
            self.statusBar().showMessage('Объем должен быть целым числом')
            err = True
        if int(self.editValue.text())<=0:
            self.statusBar().showMessage('Объем должен быть положительным числом')
            err = True

        if  self.editName.text() == "":
            self.statusBar().showMessage('Необходимо ввести описание сорта')
            err = True
        if err != True:
            params = []
            params.append(self.editName.text())
            pos=self.CBRoast.currentIndex()
            params.append(self.RoastArrayFrm[pos][0])
            pos = self.CBForm.currentIndex()
            params.append(self.FormArrayFrm[pos][0])
            params.append(self.editDescr.text())
            params.append(self.editPrice.text())
            params.append(self.editValue.text())
            self.con = sqlite3.connect(self.db_name)
            cur = self.con.cursor()
            query = '''insert into coffee (name_sort,roasting_id,form_id,description,price,value)
                       values (?,?,?,?,?,?)'''
            cur.execute(query, tuple(params))
            self.con.commit()
            self.hide()
            self.mainFrm.statusBar().showMessage('Строка добавлена в конец таблицы')
            self.mainFrm.GetData(self.db_name)

    def isinteger(self, val):
        try:
            int(val)
            return True
        except ValueError:
            return False

class MyWidget(QMainWindow, Ui_FrmMain):
    db_name = ''
    result = []
    FormArray = []
    RoastArray = []
    BtnPressed = -1
    FrmCof = None

    def __init__(self):
        super().__init__()
        #uic.loadUi('main.ui', self)
        self.setupUi(self)
        # создание окна, его название, размер;
        self.setGeometry(0, 0, 860, 400)
        self.db_name = "DATA\coffee.sqlite"
        self.labelRes.setText('')
        self.GetSprav(self.db_name)
        self.GetData(self.db_name)
        self.BtnADDForm.clicked.connect(self.add_form)
        self.BtnADDRoast.clicked.connect(self.add_roast)
        self.BtnADDCoffee.clicked.connect(self.add_coffee)
        self.FrmCof = FrmEditCoffee()
        self.FrmCof.mainFrm = self
        self.FrmCof.hide()

    def GetSprav(self, db_name):
        self.con = sqlite3.connect(self.db_name)
        cur = self.con.cursor()
        query = '''
            SELECT form_name, form_id
            from form    
            ORDER BY 1
            '''
        tmp = cur.execute(query).fetchall()
        for row in tmp:
            self.FormArray.append(row[0])
            self.FormArray.append(row[1])
        cur.close()

        query = '''
                    SELECT roast_name, roast_id
                    from roast    
                    ORDER BY 1
                    '''
        cur = self.con.cursor()
        tmp = cur.execute(query).fetchall()
        for row in tmp:
            self.RoastArray.append(row[0])
            self.RoastArray.append(row[1])
        cur.close()

    def GetData(self, db_name):
        titles = ['ID','Сорт','Форма','Обжарка','Цена', 'Объем', 'Описание']
        self.labelRes.setText('')
       # try:
        self.con = sqlite3.connect(db_name)
        cur = self.con.cursor()
        query = '''
            select coffee.id, 
                coffee.name_sort,
                form.form_name,
                roast.roast_name, 
                coffee.price,
                coffee.value,
                coffee.description
            from coffee
            left join form on form.form_id=coffee.form_id
            left join roast on roast.roast_id=coffee.roasting_id'''
        try:
            self.result = cur.execute(query).fetchall()
        except sqlite3.DatabaseError as err:
            self.labelRes.setText('Некорректный запрос')

        if self.labelRes.text() =='' and len(self.result) == 0:
            self.labelRes.setText('****** НИЧЕГО НЕ НАЙДЕНО')
        elif len(self.result) > 0:
            self.labelRes.setText('Найдено строк: '+ str(len(self.result)))
            self.tableWidgetRes.setColumnCount(7)
            self.tableWidgetRes.setRowCount(1)
            for i, elem in enumerate(titles):
                self.tableWidgetRes.setItem(0, i, QTableWidgetItem(elem))
            for i, row in enumerate(self.result):
                self.tableWidgetRes.setRowCount(self.tableWidgetRes.rowCount()+1)
                for j, elem in enumerate(row):
                    self.tableWidgetRes.setItem(i + 1, j, QTableWidgetItem(str(elem)))
                    cell = self.tableWidgetRes.item(i, j)
                    cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
            self.tableWidgetRes.resizeColumnsToContents()
        cur.close()

    def add_form(self):
        dialog = InputDialogOneField()
        dialog.WinCaption("Форма (в зернах, молотый ...)")
        dialog.setValueNames(self.FormArray)
        if dialog.exec():
            self.con = sqlite3.connect(self.db_name)
            cur = self.con.cursor()
            query = '''insert into form (form_name) values (?)'''
            params = dialog.getInputs()
            cur.execute(query, (params,))
            self.con.commit()
            self.statusBar().showMessage('Строка добавлена в конец таблицы')

    def add_roast(self):
        dialog = InputDialogOneField()
        dialog.WinCaption("Обжарка")
        dialog.setValueNames(self.RoastArray)
        if dialog.exec():
            self.con = sqlite3.connect(self.db_name)
            cur = self.con.cursor()
            query = '''insert into roast (roast_name) values (?)'''
            params = dialog.getInputs()
            cur.execute(query, (params,))
            self.con.commit()
            self.statusBar().showMessage('Строка добавлена в конец таблицы')

    def add_coffee(self):
        self.FrmCof.OnShow()
        self.FrmCof.setWindowModality(Qt.WindowModal)
        self.FrmCof.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())