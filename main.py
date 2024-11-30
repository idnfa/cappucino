import sqlite3
import sys

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QApplication, QTableWidgetItem, QHeaderView, QVBoxLayout, QHBoxLayout, QMainWindow, \
    QMessageBox


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.change_btn = None
        self.add_btn = None
        self.con = None
        self.Flag = ''
        self.tableWidget = None
        uic.loadUi('main.ui', self)

        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(
            ['ID', 'Название сорта', 'обжарка', 'помол', 'вкусовые характеристики', 'цена', 'объем упаковки']
        )
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout = QVBoxLayout(self)
        lay2 = QHBoxLayout(self)
        lay2.addWidget(self.add_btn)
        self.add_btn.clicked.connect(self.adding)
        lay2.addWidget(self.change_btn)
        self.change_btn.clicked.connect(self.changing)
        layout.addLayout(lay2)
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        self.con = sqlite3.connect('coffee.sqlite')
        cur = self.con.cursor()
        cur.execute("""
            SELECT ID, name, roasting, grinding, taste, price, volume FROM coffee
        """)
        rows = cur.fetchall()
        self.tableWidget.setRowCount(0)
        for row in rows:
            self.tableWidget.insertRow(self.tableWidget.rowCount())
            for col, item in enumerate(row):
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, col, QTableWidgetItem(str(item)))
                if col == 0:
                    self.tableWidget.item(self.tableWidget.rowCount() - 1, col).setFlags(Qt.ItemFlag.ItemIsEditable)

        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()

    def adding(self):
        self.Flag = 'add'
        self.new_form = NewWidget(self)
        self.new_form.show()

    def changing(self):
        self.Flag = 'change'
        self.new_form = NewWidget(self)
        self.new_form.id_line.setEnabled(True)
        self.new_form.show()


class NewWidget(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.statuslabel = None
        self.verd_btn = None
        self.volume_line = None
        self.price_line = None
        self.taste_line = None
        self.grind_box = None
        self.roast_box = None
        self.name_line = None
        self.id_line = None
        self.con = None
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.verd_btn.clicked.connect(self.act)
        if self.parent().Flag == 'add':
            self.id_line.setEnabled(False)

    def act(self):
        id = self.id_line.text()
        name = self.name_line.text()
        roasting = self.roast_box.currentText()
        grinding = self.grind_box.currentText()
        info = self.taste_line.text()
        price = self.price_line.text()
        volume = self.volume_line.text()
        self.con = sqlite3.connect('coffee.sqlite')
        cursor = self.con.cursor()
        if (not name or not info or not price or not volume) or (not id and self.parent().Flag == 'change'):
            self.statuslabel.setText('Неверно заполнена форма')
            return False
        try:
            if self.parent().Flag == 'change':
                test = int(id)
            test = int(price)
            test = int(volume)
            if test <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, 'Предупреждение',
                                 f'Значение ID, цены, объема может быть только целым положительным числом')
            self.load_data()
            return False
        if self.parent().Flag == 'change':
            ids = cursor.execute("""SELECT id FROM coffee WHERE id = ?""", (id,)).fetchall()
            if not ids:
                QMessageBox.critical(self, 'Предупреждение',
                                     f'Нет элемента с таким ID')
                return False
        if self.parent().Flag == 'add':
            try:
                cursor.execute(
                    "INSERT INTO coffee (name, roasting, grinding, taste, price,volume) VALUES"
                    " (?, ?, ?, ?, ?, ?)",
                    (name, roasting, grinding, info, price, volume))
                self.con.commit()
                QMessageBox.information(self, 'Успех', 'Кофе добавлен!')
                self.statuslabel.setText('')
                self.parent().load_data()
                self.close()
                return True

            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось добавить: {str(e)}')
                return False

        elif self.parent().Flag == 'change':
            try:
                cursor.execute("""
                            UPDATE coffee
                            SET name = ?, roasting = ?, grinding = ?, taste = ?, price = ?, volume = ?
                            WHERE id = ?
                        """, (name, roasting, grinding, info, price, volume, id))
                self.con.commit()
                QMessageBox.information(self, 'Успех', 'Кофе изменен!')
                self.statuslabel.setText('')
                self.parent().load_data()
                self.close()
                return True

            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить: {str(e)}')
                return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())