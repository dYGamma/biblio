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
        'icon_name': 'fa5s.moon',
    },
    'light_cyan_500': {
        'text_color': '#212121',
        'input_text_color': '#212121',
        'input_focus_color': '#00bcd4',
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
    qss = f"""
        QLineEdit, QDateEdit, QTimeEdit, QComboBox {{
            color: {p['input_text_color']};
        }}
        QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {{
            color: {p['input_focus_color']};
        }}
        QLineEdit::placeholder {{ color: #888888; }}
        QComboBox QAbstractItemView {{
            color: {p['text_color']};
            background-color: transparent;
            selection-background-color: {p['input_focus_color']};
            selection-color: #ffffff;
        }}
        QSpinBox, QDoubleSpinBox {{
            color: {p['input_text_color']};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            color: {p['input_focus_color']};
            border: 1px solid {p['input_focus_color']};
            border-radius: 4px;
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