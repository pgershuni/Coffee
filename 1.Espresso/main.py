import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtCore import Qt

class MyWidget(QMainWindow):
    db_name = ''
    result = []

    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        # создание окна, его название, размер;
        self.setGeometry(0, 0, 860, 400)
        self.db_name = "coffee.sqlite"
        self.labelRes.setText('')
        self.GetData(self.db_name)

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
        self.result = cur.execute(query).fetchall()
        #except sqlite3.DatabaseError as err:
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())