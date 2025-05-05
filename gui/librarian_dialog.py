from PyQt5 import QtWidgets
from gui.user_dialog import UserDialog

class LibrarianDialog(UserDialog):
    def __init__(self, user=None):
        super().__init__(user=user, role_fixed='librarian')
        self.setWindowTitle("Библиотекарь")
