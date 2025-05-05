import sys, os, logging.config
from PyQt5.QtWidgets import QApplication
from database import init_db
from gui.login_dialog import LoginDialog
from gui.dashboard_window import MainWindow

def main():
    init_db()
    base = os.path.abspath(os.path.dirname(__file__))
    os.makedirs(os.path.join(base,'logs'),exist_ok=True)
    log_conf = os.path.join(base,'config','log_config.ini')
    print(f"[Debug] Loading log config: {log_conf}")
    if os.path.exists(log_conf):
        logging.config.fileConfig(log_conf, disable_existing_loggers=False)
    app = QApplication(sys.argv)
    from utils.theme_manager import init_theme
    init_theme()
    login = LoginDialog()
    if login.exec_() != LoginDialog.Accepted:
        sys.exit(0)
    win = MainWindow(login.user, lambda: LoginDialog())
    # win.show()
    win.showFullScreen()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()
