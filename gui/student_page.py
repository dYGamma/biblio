# gui/student_page.py

from PyQt5 import QtWidgets, QtCore
from datetime import timedelta
import controllers

class StudentPage(QtWidgets.QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

        layout = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.tabs)

        # Вкладки
        self.tab_search = QtWidgets.QWidget()
        self._init_search_tab()
        self.tabs.addTab(self.tab_search, "Поиск книг")

        self.tab_my = QtWidgets.QWidget()
        self._init_my_tab()
        self.tabs.addTab(self.tab_my, "Мои заказы")

        # При смене вкладки — обновляем содержимое
        self.tabs.currentChanged.connect(self._on_tab_changed)

        # Первичная загрузка
        self.on_search()
        self.reload_my_orders()

    def _init_search_tab(self):
        v = QtWidgets.QVBoxLayout(self.tab_search)
        hl = QtWidgets.QHBoxLayout()
        self.le_search = QtWidgets.QLineEdit()
        self.le_search.setPlaceholderText("Введите название книги...")
        btn = QtWidgets.QPushButton("Найти")
        btn.clicked.connect(self.on_search)
        hl.addWidget(self.le_search)
        hl.addWidget(btn)
        v.addLayout(hl)

        self.table_search = QtWidgets.QTableWidget(0, 5)
        self.table_search.setHorizontalHeaderLabels(
            ["ID", "Название", "Автор", "Копий", "Заказать"]
        )
        self.table_search.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        v.addWidget(self.table_search)

    def _init_my_tab(self):
        v = QtWidgets.QVBoxLayout(self.tab_my)
        self.table_my = QtWidgets.QTableWidget(0, 6)
        self.table_my.setHorizontalHeaderLabels(
            ["ID заказа", "Название", "Дата выдачи", "Срок сдачи", "Статус", "Вернуть"]
        )
        self.table_my.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        v.addWidget(self.table_my)

    def _translate_status(self, status: str) -> str:
        translations = {
            "pending":   "В ожидании подтверждения",
            "issued":    "Выдана",
            "overdue":   "Просрочена",
            "returned":  "Возвращена",
            "cancelled": "Отменена",
        }
        return translations.get(status, status)

    def _on_tab_changed(self, index: int):
        # Если открыли вкладку Поиск — обновляем список книг
        if self.tabs.widget(index) is self.tab_search:
            self.on_search()
        # Если вкладку «Мои заказы»
        elif self.tabs.widget(index) is self.tab_my:
            self.reload_my_orders()

    def on_search(self):
        term = self.le_search.text().strip().lower()
        books = controllers.find_books()
        if term:
            books = [b for b in books if term in b.title.lower()]

        self.table_search.setRowCount(0)
        for b in books:
            i = self.table_search.rowCount()
            self.table_search.insertRow(i)
            self.table_search.setItem(i, 0, QtWidgets.QTableWidgetItem(str(b.id)))
            self.table_search.setItem(i, 1, QtWidgets.QTableWidgetItem(b.title))
            self.table_search.setItem(i, 2, QtWidgets.QTableWidgetItem(b.author))
            self.table_search.setItem(i, 3, QtWidgets.QTableWidgetItem(str(b.copies)))
            btn = QtWidgets.QPushButton("Заказать")
            btn.clicked.connect(lambda _, bid=b.id: self._order(bid))
            self.table_search.setCellWidget(i, 4, btn)

    def _order(self, book_id):
        try:
            controllers.create_order(self.user_id, book_id)
            QtWidgets.QMessageBox.information(
                self, "Успех", "Книга успешно заказана! Ждите подтверждения."
            )
            # После заказа сразу обновим обе таблицы
            self.on_search()
            self.reload_my_orders()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка при заказе", str(e))

    def reload_my_orders(self):
        orders = controllers.list_orders_for_user(self.user_id)
        self.table_my.setRowCount(0)
        for o in orders:
            i = self.table_my.rowCount()
            self.table_my.insertRow(i)

            issue_str = o.issue_date.strftime("%Y-%m-%d") if o.issue_date else ""
            due_str   = o.due_date.strftime("%Y-%m-%d")   if getattr(o, 'due_date', None) else ""
            status_str = self._translate_status(o.status)

            self.table_my.setItem(i, 0, QtWidgets.QTableWidgetItem(str(o.id)))
            self.table_my.setItem(i, 1, QtWidgets.QTableWidgetItem(o.book.title))
            self.table_my.setItem(i, 2, QtWidgets.QTableWidgetItem(issue_str))
            self.table_my.setItem(i, 3, QtWidgets.QTableWidgetItem(due_str))
            self.table_my.setItem(i, 4, QtWidgets.QTableWidgetItem(status_str))

            btn = QtWidgets.QPushButton("Вернуть")
            can_return = o.issue_date is not None and o.status != "returned"
            btn.setEnabled(can_return)
            btn.clicked.connect(lambda _, oid=o.id: self._return(oid))
            self.table_my.setCellWidget(i, 5, btn)

    def _return(self, order_id: int):
        try:
            controllers.return_order(order_id)
            QtWidgets.QMessageBox.information(
                self, "Успех", "Книга помечена как возвращённая."
            )
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка при возврате", str(e))
        finally:
            # и тут тоже сразу обновляем
            self.reload_my_orders()
            # а если студент вернулся на вкладку «Поиск», чтобы увидеть остаток —
            # можно раскомментировать:
            # self.on_search()

    # Также гарантируем обновление при каждом показе:
    def showEvent(self, event):
        super().showEvent(event)
        current = self.tabs.currentIndex()
        self._on_tab_changed(current)
