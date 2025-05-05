# gui/login_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout,
    QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import controllers

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добро пожаловать в библиотеку")
        self.setWindowIcon(QIcon(":/icons/library.png"))   # если есть ресурс с иконкой
        self.setFixedSize(350, 260)

        # Заголовок
        header = QLabel("Пожалуйста, войдите")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setContentsMargins(0, 20, 0, 20)

        # Поля ввода в форме
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form.setHorizontalSpacing(15)
        form.setVerticalSpacing(15)

        self.user_id = QLineEdit()
        self.user_id.setPlaceholderText("ID ученика или библиотекаря")
        self.user_id.setMinimumWidth(200)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Ваш пароль")

        form.addRow("Логин:", self.user_id)
        form.addRow("Пароль:", self.password)

        # Кнопки
        btn_login = QPushButton("Войти")
        btn_login.setDefault(True)
        btn_login.clicked.connect(self.attempt_login)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_login)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addStretch()

        # Собираем всё вместе
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(header)
        main_layout.addLayout(form)
        main_layout.addSpacing(20)
        main_layout.addLayout(btn_layout)
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.user = None

    def attempt_login(self):
        # Сбрасываем стили полей
        self.user_id.setStyleSheet("")
        self.password.setStyleSheet("")

        uid = self.user_id.text().strip()
        pw  = self.password.text().strip()
        if not uid or not pw:
            QMessageBox.information(self, "Заполните поля", "Пожалуйста, введите логин и пароль.")
            return

        role = controllers.authenticate(uid, pw)
        if role:
            self.user = controllers.get_user(uid)
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {self.user.name}!")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка входа", "Неверный логин или пароль.")
            self.user_id.setStyleSheet("border: 1px solid red;")
            self.password.setStyleSheet("border: 1px solid red;")
            self.user_id.setFocus()
