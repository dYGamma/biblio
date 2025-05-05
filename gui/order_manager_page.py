# gui/order_manager_page.py

from PyQt5 import QtWidgets, QtCore
import controllers
import functools
from datetime import datetime

class OrderManagerPage(QtWidgets.QWidget):
    reload_request = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)

        # Кнопка обновления
        btn_refresh = QtWidgets.QPushButton("Обновить")
        btn_refresh.clicked.connect(self.reload)
        layout.addWidget(btn_refresh)

        # Активные заказы
        lbl_active = QtWidgets.QLabel("Активные заказы")
        lbl_active.setStyleSheet("font-size:16px; font-weight:bold; margin:8px 0;")
        layout.addWidget(lbl_active)

        self.table_active = QtWidgets.QTableWidget(0, 12)
        headers_active = [
            "ID", "Ученик", "Книга", "Статус", "Заявка",
            "Одобрение", "Выдача", "Срок",
            "→ Действие", "Подтвердить", "Выдать", "Установить срок"
        ]
        self.table_active.setHorizontalHeaderLabels(headers_active)
        hh1 = self.table_active.horizontalHeader()
        # Первые 8 колонок по содержимому
        for col in range(0, 8):
            hh1.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
        # Колонка "→ Действие"
        hh1.setSectionResizeMode(8, QtWidgets.QHeaderView.ResizeToContents)
        # Колонки с виджетами растягиваем
        for col in (9, 10, 11):
            hh1.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            # Минимальная ширина, чтобы не «урезало»
            self.table_active.setColumnWidth(col, 180)

        self.table_active.verticalHeader().setVisible(False)
        layout.addWidget(self.table_active)

        # Возвращённые заказы
        lbl_returned = QtWidgets.QLabel("Возвращённые заказы")
        lbl_returned.setStyleSheet("font-size:16px; font-weight:bold; margin:16px 0 8px;")
        layout.addWidget(lbl_returned)

        self.table_returned = QtWidgets.QTableWidget(0, 5)
        self.table_returned.setHorizontalHeaderLabels([
            "ID заказа", "Ученик", "Книга", "Срок сдачи", "Дата возврата"
        ])
        self.table_returned.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table_returned.verticalHeader().setVisible(False)
        layout.addWidget(self.table_returned)

        # Первая загрузка
        self.reload()

    def _translate_status(self, status: str) -> str:
        mapping = {
            'pending':   'В ожидании',
            'confirmed': 'Подтвержено',
            'issued':    'Выдана',
            'overdue':   'Просрочена',
            'returned':  'Возвращена',
            'cancelled': 'Отменена',
        }
        return mapping.get(status, status)

    def reload(self):
        self.table_active.setRowCount(0)
        self.table_returned.setRowCount(0)

        orders = controllers.list_all_orders()
        for o in orders:
            st = o.status

            if st == 'returned':
                # Заполняем возвращённые заказы
                r = self.table_returned.rowCount()
                self.table_returned.insertRow(r)
                due = o.due_date.strftime("%Y-%m-%d") if o.due_date else ""
                ret = o.return_date.strftime("%Y-%m-%d") if getattr(o, 'return_date', None) else ""
                for col, val in enumerate([o.id, o.user_id, o.book.title, due, ret]):
                    item = QtWidgets.QTableWidgetItem(str(val))
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.table_returned.setItem(r, col, item)
                continue

            # Активные заказы
            r = self.table_active.rowCount()
            self.table_active.insertRow(r)

            fields = [
                o.id,
                o.user_id,
                o.book.title,
                self._translate_status(o.status),
                o.request_date.strftime("%Y-%m-%d") if o.request_date else "",
                o.confirm_date.strftime("%Y-%m-%d") if getattr(o, 'confirm_date', None) else "",
                o.issue_date.strftime("%Y-%m-%d") if o.issue_date else "",
                o.due_date.strftime("%Y-%m-%d") if getattr(o, 'due_date', None) else ""
            ]
            for col, val in enumerate(fields):
                item = QtWidgets.QTableWidgetItem(str(val))
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                self.table_active.setItem(r, col, item)

            # Кнопка → переход в следующий статус
            btn_action = QtWidgets.QPushButton("→")
            btn_action.clicked.connect(functools.partial(self._next, o.id))
            if st == 'issued':
                ready = bool(o.issue_date and getattr(o, 'due_date', None))
                btn_action.setEnabled(ready)
            self.table_active.setCellWidget(r, 8, btn_action)

            # Виджеты установки дат
            def mk(col, text, fn):
                date_edit = QtWidgets.QDateEdit(calendarPopup=True)
                date_edit.setDate(QtCore.QDate.currentDate())
                date_edit.setSizePolicy(
                    QtWidgets.QSizePolicy.Expanding,
                    QtWidgets.QSizePolicy.Fixed
                )
                btn = QtWidgets.QPushButton(text)
                btn.setSizePolicy(
                    QtWidgets.QSizePolicy.Expanding,
                    QtWidgets.QSizePolicy.Fixed
                )
                btn.clicked.connect(
                    lambda _, oid=o.id, w=date_edit: self._set_date(fn, oid, w.date().toPyDate())
                )

                wdg = QtWidgets.QWidget()
                wdg.setSizePolicy(
                    QtWidgets.QSizePolicy.Expanding,
                    QtWidgets.QSizePolicy.Fixed
                )
                hl = QtWidgets.QHBoxLayout(wdg)
                hl.setContentsMargins(2, 2, 2, 2)
                hl.setSpacing(4)
                hl.addWidget(date_edit)
                hl.addWidget(btn)
                self.table_active.setCellWidget(r, col, wdg)

            mk(9,  "Подтвердить", controllers.set_confirm_date)
            mk(10, "Выдать",      controllers.set_issue_date)
            mk(11, "Установить срок", controllers.set_due_date)

        # Оповестить, чтобы студентская страница обновилась
        self.reload_request.emit()

    def _next(self, order_id):
        try:
            controllers.advance_order(order_id)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка", str(e))
        finally:
            self.reload()
            self.reload_request.emit()

    def _set_date(self, controller_fn, order_id, date_obj):
        try:
            dt = datetime.combine(date_obj, datetime.min.time())
            controller_fn(order_id, dt)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка", str(e))
        finally:
            self.reload()
            self.reload_request.emit()
