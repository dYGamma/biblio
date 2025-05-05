from PyQt5 import QtWidgets, QtCore

class UserDialog(QtWidgets.QDialog):
    def __init__(self, user=None, role_fixed=None):
        super().__init__()
        self.setWindowTitle("Пользователь")
        self.user = user
        self.role_fixed = role_fixed
        self.role_translations = {
            "student": "ученик",
            "librarian": "библиотекарь",
            "admin": "администратор"
        }

        # Поля формы
        self.le_id = QtWidgets.QLineEdit()
        self.le_name = QtWidgets.QLineEdit()
        self.le_clazz = QtWidgets.QLineEdit()
        self.le_pw = QtWidgets.QLineEdit()
        self.le_pw.setEchoMode(QtWidgets.QLineEdit.Password)

        # Виджет роли
        if role_fixed:
            translated_role = self.role_translations.get(role_fixed, role_fixed)
            self.role_widget = QtWidgets.QLabel(translated_role.capitalize())
        else:
            self.role_widget = QtWidgets.QComboBox()
            self.role_widget.addItem("ученик", "student")
            self.role_widget.addItem("библиотекарь", "librarian")
            self.role_widget.currentTextChanged.connect(self.on_role_changed)

        # Построение формы
        form = QtWidgets.QFormLayout(self)
        form.addRow("ID:", self.le_id)
        form.addRow("ФИО:", self.le_name)
        form.addRow("Роль:", self.role_widget)
        form.addRow("Класс:", self.le_clazz)
        form.addRow("Пароль:", self.le_pw)

        # Кнопки
        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

        # Заполнение данных при редактировании
        if user:
            self.le_id.setText(user.id)
            self.le_id.setReadOnly(True)
            self.le_name.setText(user.name)
            self.le_clazz.setText(user.clazz or "")
            if not role_fixed:
                idx = self.role_widget.findData(user.role)
                if idx >= 0:
                    self.role_widget.setCurrentIndex(idx)

        # Обновление видимости поля "Класс"
        initial_role = role_fixed or (
            user.role if user else self.role_widget.currentData()
        )
        self._update_class_visibility(initial_role)

    def on_role_changed(self, new_role: str):
        self._update_class_visibility(self.role_widget.currentData())

    def _update_class_visibility(self, role: str):
        """Скрывает/показывает поле класса в зависимости от роли"""
        is_student = (role == "student")
        self.le_clazz.setVisible(is_student)
        form = self.layout()
        for i in range(form.rowCount()):
            label_item = form.itemAt(i, QtWidgets.QFormLayout.LabelRole)
            field_item = form.itemAt(i, QtWidgets.QFormLayout.FieldRole)
            if field_item and field_item.widget() is self.le_clazz:
                label_item.widget().setVisible(is_student)
                field_item.widget().setVisible(is_student)
                break

    def get_data(self):
        """Возвращает данные формы в виде словаря"""
        return {
            'id': self.le_id.text().strip(),
            'name': self.le_name.text().strip(),
            'password': self.le_pw.text().strip() or None,
            'role': self.role_fixed or self.role_widget.currentData(),
            'clazz': self.le_clazz.text().strip() if (
                self.role_fixed == "student" or 
                (self.role_widget.currentData() == "student")
            ) else None
        }