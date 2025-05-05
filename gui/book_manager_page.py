# gui/book_manager_page.py

from PyQt5 import QtWidgets, QtCore
from gui.book_dialog import BookDialog
import controllers

class BookManagerPage(QtWidgets.QWidget):
    # Вернём сигнал, чтобы другие страницы (например, Orders) знали об обновлениях
    data_changed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        v = QtWidgets.QVBoxLayout(self)
        # CRUD-кнопки
        hb = QtWidgets.QHBoxLayout()
        self.btn_add  = QtWidgets.QPushButton("Добавить")
        self.btn_edit = QtWidgets.QPushButton("Редактировать")
        self.btn_del  = QtWidgets.QPushButton("Удалить")
        hb.addWidget(self.btn_add)
        hb.addWidget(self.btn_edit)
        hb.addWidget(self.btn_del)
        v.addLayout(hb)

        # Таблица
        self.table = QtWidgets.QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["ID","ISBN","Название","Автор","Жанр","Год","Копий"]
        )
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        v.addWidget(self.table)

        # Связываем сигналы кнопок
        self.btn_add.clicked.connect(self.add_book)
        self.btn_edit.clicked.connect(self.edit_book)
        self.btn_del.clicked.connect(self.del_book)

        # Первичная загрузка
        self.reload()

    def reload(self):
        self.table.setRowCount(0)
        for b in controllers.find_books():
            i = self.table.rowCount()
            self.table.insertRow(i)
            for col, v in enumerate([b.id, b.isbn, b.title, b.author, b.genre, b.year, b.copies]):
                self.table.setItem(i, col, QtWidgets.QTableWidgetItem(str(v)))
        # Уведомляем подписчиков об изменении данных
        self.data_changed.emit()

    def add_book(self):
        dlg = BookDialog()
        if dlg.exec_():
            controllers.create_book(dlg.get_data())
            self.reload()

    def edit_book(self):
        r = self.table.currentRow()
        if r < 0:
            return
        bid = int(self.table.item(r, 0).text())
        book = controllers.get_book(bid)
        dlg = BookDialog(book=book)
        if dlg.exec_():
            controllers.update_book(bid, dlg.get_data())
            self.reload()

    def del_book(self):
        r = self.table.currentRow()
        if r < 0:
            return
        bid = int(self.table.item(r, 0).text())
        controllers.delete_book(bid)
        self.reload()
