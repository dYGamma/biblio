# gui/dashboard_window.py
_app_context = {}
from PyQt5 import QtWidgets, QtCore
from utils.theme_manager import toggle_theme, update_theme_ui
from gui.book_manager_page import BookManagerPage
from gui.order_manager_page import OrderManagerPage
from gui.report_page import ReportPage
from gui.user_manager_page import UserManagerPage
from gui.librarian_manager_page import LibrarianManagerPage
from gui.student_page import StudentPage
import logging

logger = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, user, make_login_dialog):
        super().__init__()
        self.user = user
        self.make_login_dialog = make_login_dialog

        # ---
        self.setWindowTitle(f"Школьная библиотека — {user.role.capitalize()}")
        self.resize(1920, 1080)

        # Верхний бар
        top_bar = QtWidgets.QWidget()
        hl = QtWidgets.QHBoxLayout(top_bar)
        hl.setContentsMargins(8,8,8,4)
        hl.setSpacing(4)

        # Навигация
        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setExpanding(True)
        self.tab_bar.setDrawBase(False)
        self.stack = QtWidgets.QStackedWidget()

        if user.role == 'student':
            # Студент
            self.tab_bar.addTab("🔍 Поиск и Заказы")
            self.page_student = StudentPage(user.id)
            self.stack.addWidget(self.page_student)

        else:
            # 1. Каталог книг
            self.tab_bar.addTab("📚 Каталог книг")
            self.page_books = BookManagerPage()
            self.stack.addWidget(self.page_books)

            # 2. Заказы
            self.tab_bar.addTab("🔖 Заказы")
            self.page_orders = OrderManagerPage()
            self.stack.addWidget(self.page_orders)

            # — нажатие кнопок в заказах обновляет каталог
            self.page_orders.reload_request.connect(self.page_books.reload)

            # 3. Отчёты
            self.tab_bar.addTab("📑 Отчёты")
            self.page_reports = ReportPage()
            self.stack.addWidget(self.page_reports)

            # 4. Пользователи / библиотекари
            if user.role == 'librarian':
                self.tab_bar.addTab("👥 Пользователи")
                self.page_users = UserManagerPage()
                self.stack.addWidget(self.page_users)
            if user.role == 'admin':
                self.tab_bar.addTab("🛠 Библиотекари")
                self.page_libs = LibrarianManagerPage()
                self.stack.addWidget(self.page_libs)

        # Переключение табов
        self.tab_bar.currentChanged.connect(self.on_nav_changed)
        hl.addWidget(self.tab_bar, stretch=1)

        # Кнопки справа
        btn_switch = QtWidgets.QPushButton()
        btn_switch.setFixedSize(32,32)
        btn_switch.clicked.connect(self.on_switch_account)
        hl.addWidget(btn_switch, QtCore.Qt.AlignRight)

        btn_theme = QtWidgets.QPushButton()
        btn_theme.setFixedSize(32,32)
        btn_theme.clicked.connect(lambda: toggle_theme(btn_theme, None, btn_switch))
        hl.addWidget(btn_theme, QtCore.Qt.AlignRight)

        update_theme_ui(btn_theme, None, btn_switch)

        # Центральный виджет
        central = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(central)
        vbox.setContentsMargins(0,0,0,0)
        vbox.setSpacing(0)
        vbox.addWidget(top_bar)
        vbox.addWidget(self.stack)
        self.setCentralWidget(central)

        # Показать первый таб
        self.tab_bar.setCurrentIndex(0)
        self.stack.setCurrentIndex(0)

        logger.info("MainWindow initialized for %s", user.id)

    def on_nav_changed(self, index: int):
        self.stack.setCurrentIndex(index)

    def on_switch_account(self):
        dlg = self.make_login_dialog()
        if dlg.exec_():
            new_user = dlg.user
            from gui.dashboard_window import MainWindow

            # создаём и сохраняем ссылку на новое окно
            new_win = MainWindow(new_user, self.make_login_dialog)
            _app_context["main_window"] = new_win  # сохранили, чтобы не удалился

            # new_win.show()
            new_win.showFullScreen()
            self.close()
