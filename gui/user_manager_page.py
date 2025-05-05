# gui/user_manager_page.py

from PyQt5 import QtWidgets, QtCore
from gui.user_dialog import UserDialog
import controllers
from sqlalchemy.exc import IntegrityError

class UserManagerPage(QtWidgets.QWidget):
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

        # Таблица пользователей
        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Роль", "Класс"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        v.addWidget(self.table)

        # Подключаем сигналы
        self.btn_add.clicked.connect(self.add_user)
        self.btn_edit.clicked.connect(self.edit_user)
        self.btn_del.clicked.connect(self.del_user)

        self.role_translations = {  # Добавляем словарь переводов
            "student": "ученик",
            "librarian": "библиотекарь",
            "admin": "администратор"
        }

        self.reload()

    def reload(self):
        self.table.setRowCount(0)
        for u in controllers.list_users():
            i = self.table.rowCount()
            self.table.insertRow(i)
            translated_role = self.role_translations.get(u.role, u.role)
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(u.id))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(u.name))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(translated_role))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(u.clazz or ""))

    def add_user(self):
        dlg = UserDialog(role_fixed=None)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            data = dlg.get_data()
            try:
                controllers.create_user(**data)
            except IntegrityError:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Пользователь с ID «{data['id']}» уже существует."
                )
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Не удалось создать пользователя:\n{e}"
                )
            finally:
                self.reload()

    def edit_user(self):
        r = self.table.currentRow()
        if r < 0:
            return
        uid = self.table.item(r, 0).text()
        u = controllers.get_user(uid)
        dlg = UserDialog(user=u, role_fixed=u.role)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            data = dlg.get_data()
            try:
                controllers.update_user(uid, **data)
            except IntegrityError:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Нельзя изменить ID на «{data['id']}» — такой уже есть."
                )
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Не удалось обновить пользователя:\n{e}"
                )
            finally:
                self.reload()

    def del_user(self):
        r = self.table.currentRow()
        if r < 0:
            return
        uid = self.table.item(r, 0).text()
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Подтвердите удаление",
            f"Удалить пользователя «{uid}»?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirm == QtWidgets.QMessageBox.Yes:
            try:
                controllers.delete_user(uid)
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Не удалось удалить пользователя:\n{e}"
                )
            finally:
                self.reload()
