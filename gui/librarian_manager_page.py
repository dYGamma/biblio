from PyQt5 import QtWidgets
from gui.librarian_dialog import LibrarianDialog
import controllers

class LibrarianManagerPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        v=QtWidgets.QVBoxLayout(self)
        hb=QtWidgets.QHBoxLayout()
        self.btn_add=QtWidgets.QPushButton("Добавить")
        self.btn_edit=QtWidgets.QPushButton("Редактировать")
        self.btn_del=QtWidgets.QPushButton("Удалить")
        hb.addWidget(self.btn_add); hb.addWidget(self.btn_edit); hb.addWidget(self.btn_del)
        v.addLayout(hb)
        self.table=QtWidgets.QTableWidget(0,4)
        self.table.setHorizontalHeaderLabels(["ID","ФИО","Роль","Класс"])
        hh=self.table.horizontalHeader(); hh.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        v.addWidget(self.table)
        self.btn_add.clicked.connect(self.add_lib)
        self.btn_edit.clicked.connect(self.edit_lib)
        self.btn_del.clicked.connect(self.del_lib)
        self.reload()

    def reload(self):
        self.table.setRowCount(0)
        for u in controllers.list_users(role='librarian'):
            i=self.table.rowCount(); self.table.insertRow(i)
            for c,v in enumerate([u.id,u.name,u.role,u.clazz]):
                self.table.setItem(i,c,QtWidgets.QTableWidgetItem(str(v)))

    def add_lib(self):
        dlg=LibrarianDialog()
        if dlg.exec_():
            controllers.create_user(**dlg.get_data()); self.reload()

    def edit_lib(self):
        r=self.table.currentRow()
        if r<0: return
        uid=self.table.item(r,0).text()
        u=controllers.get_user_obj(uid)
        dlg=LibrarianDialog(user=u)
        if dlg.exec_():
            controllers.update_user(uid, **dlg.get_data()); self.reload()

    def del_lib(self):
        r=self.table.currentRow()
        if r<0: return
        controllers.delete_user(self.table.item(r,0).text()); self.reload()
