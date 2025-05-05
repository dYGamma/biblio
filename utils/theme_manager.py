from qt_material import apply_stylesheet
from PyQt5.QtWidgets import QApplication
import qtawesome as qta
from configparser import ConfigParser
import os

THEMES = {
    'dark_teal': 'dark_teal.xml',
    'light_cyan_500': 'light_cyan_500.xml',
}

theme_params = {
    'dark_teal': {
        'text_color': '#cccccc',
        'input_text_color': '#cccccc',
        'input_focus_color': '#00bcd4',
        'background_color': '#263238',
        'icon_name': 'fa5s.moon',
    },
    'light_cyan_500': {
        'text_color': '#212121',
        'input_text_color': '#212121',
        'input_focus_color': '#00bcd4',
        'background_color': '#f5f5f5',  # <--- добавлено
        'icon_name': 'fa5s.sun',
    },
}

current_theme = None

def init_theme():
    """Устанавливает тему при старте приложения."""
    global current_theme
    cfg = ConfigParser()
    cfg.read(os.path.join('config', 'config.ini'))
    theme_name = cfg.get('app', 'theme', fallback='dark_teal')
    current_theme = theme_name
    _apply(theme_name)

def toggle_theme(theme_btn, title_lbl=None, switch_btn=None):
    """Переключает тему и обновляет UI."""
    global current_theme
    new = 'light_cyan_500' if current_theme == 'dark_teal' else 'dark_teal'
    current_theme = new
    _apply(new)
    update_theme_ui(theme_btn, title_lbl, switch_btn)

def _apply(name):
    """Применяем тему и добавляем QSS для полей ввода."""
    app = QApplication.instance()
    apply_stylesheet(app, theme=THEMES[name])
    _append_input_styles()

def _append_input_styles():
    app = QApplication.instance()
    p = theme_params[current_theme]
    bg = p['background_color']
    focus = p['input_focus_color']
    text = p['text_color']
    qss = f"""
        /* Фоновый цвет для главных виджетов */
        QWidget, QMainWindow {{
            background-color: {bg};
        }}
        QDialog, QMenuBar, QMenu, QStatusBar {{
            background-color: {bg};
        }}

        /* Текстовые поля и комбобоксы */
        QLineEdit, QDateEdit, QTimeEdit, QComboBox {{
            color: {p['input_text_color']};
        }}
        QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {{
            color: {focus};
            border: 1px solid {focus};
            border-radius: 4px;
        }}
        QLineEdit::placeholder {{ color: #888888; }}
        QComboBox QAbstractItemView {{
            color: {text};
            background-color: {bg};
            selection-background-color: {focus};
            selection-color: #ffffff;
        }}

        /* SpinBox */
        QSpinBox, QDoubleSpinBox {{
            color: {p['input_text_color']};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            color: {focus};
            border: 1px solid {focus};
            border-radius: 4px;
        }}

        /* Кнопки */
        QPushButton, QToolButton {{
            color: {text};
            background-color: transparent;
            border: 1px solid {text};
            border-radius: 6px;
            padding: 4px 8px;
        }}
        QPushButton:hover, QToolButton:hover {{
            border-color: {focus};
            background-color: rgba(0, 0, 0, 0.2);
        }}
        QPushButton:pressed, QToolButton:pressed {{
            background-color: rgba(0, 0, 0, 0.3);
        }}
        QPushButton:focus, QToolButton:focus {{
            outline: none;
            border: 1px solid {focus};
        }}
    """
    app.setStyleSheet(app.styleSheet() + qss)

def update_theme_ui(theme_btn, title_lbl=None, switch_btn=None):
    """
    Обновляет иконки и стили под текущую тему.
    title_lbl — QLabel заголовка (может быть None).
    switch_btn — кнопка выхода/смены (может быть None).
    """
    p = theme_params[current_theme]
    # иконка темы
    theme_btn.setIcon(qta.icon(p['icon_name'], color=p['text_color']))
    # стилизация заголовка, если QLabel передан
    if title_lbl is not None:
        title_lbl.setStyleSheet(f"""
            color: {p['text_color']};
            font-size: 16px;
            font-weight: bold;
            border: 2px solid {p['text_color']};
            padding: 8px;
            border-radius: 8px;
        """)
    # иконка кнопки выхода/смены
    if switch_btn is not None:
        switch_btn.setIcon(qta.icon('fa5s.sign-out-alt', color=p['text_color']))