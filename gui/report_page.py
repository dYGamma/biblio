from PyQt5 import QtWidgets, QtCore
import controllers
from datetime import datetime, timedelta

# Для поиска системных шрифтов
from matplotlib import font_manager as fm

# ReportLab для PDF
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet

# OpenPyXL для Excel
from openpyxl import Workbook
from openpyxl.styles import Font


def _find_cyrillic_font():
    patterns = ("dejavusans", "arial", "freesans", "ptserif", "freeserif")
    for font_path in fm.findSystemFonts(fontpaths=None, fontext='ttf'):
        try:
            prop = fm.FontProperties(fname=font_path)
            name = prop.get_name().lower()
            if any(p in name for p in patterns):
                return font_path
        except Exception:
            continue
    return None


def generate_low_stock_pdf(books, filename: str):
    font_path = _find_cyrillic_font()
    if not font_path:
        raise RuntimeError(
            "Не удалось найти шрифт с поддержкой кириллицы на системе. "
            "Установите DejaVuSans или Arial."
        )
    pdfmetrics.registerFont(TTFont("SysCyr", font_path))

    doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    style_header = styles['Heading1']
    style_header.fontName = 'SysCyr'
    style_normal = styles['Normal']
    style_normal.fontName = 'SysCyr'

    elements = [Paragraph("Отчёт: низкий остаток книг", style_header), Spacer(1, 0.5*cm)]

    data = [["ID", "Название", "Автор", "Копий"]]
    for b in books:
        data.append([str(b.id), b.title, b.author, str(b.copies)])

    table = Table(data, colWidths=[2*cm, 8*cm, 6*cm, 2*cm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'SysCyr'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    elements.append(table)
    doc.build(elements)


def generate_overdue_excel(orders, filename: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "Просроченные"

    header = ["ID заказа", "ID ученика", "Название", "Статус", "Дата выдачи"]
    ws.append(header)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for o in orders:
        ws.append([
            o.id,
            o.user_id,
            o.book.title,
            o.status.value,
            o.issue_date.strftime("%Y-%m-%d") if o.issue_date else ''
        ])
    wb.save(filename)


class ReportPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        lbl = QtWidgets.QLabel("Отчёты")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lbl.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(lbl)

        lbl_low = QtWidgets.QLabel("Книги с низким остатком (<2 коп.)")
        lbl_low.setStyleSheet("font-size:14px; margin-top:10px;")
        layout.addWidget(lbl_low)

        self.tbl_low = QtWidgets.QTableWidget(0, 4)
        self.tbl_low.setHorizontalHeaderLabels(["ID", "Название", "Автор", "Копий"])
        self.tbl_low.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.tbl_low)

        lbl_over = QtWidgets.QLabel("Просроченные заказы")
        lbl_over.setStyleSheet("font-size:14px; margin-top:12px;")
        layout.addWidget(lbl_over)

        self.tbl_over = QtWidgets.QTableWidget(0, 5)
        self.tbl_over.setHorizontalHeaderLabels([
            "ID заказа", "Ученик", "Книга", "Статус", "Дата выдачи"
        ])
        self.tbl_over.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.tbl_over)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        self.btn_pdf = QtWidgets.QPushButton("Сохранить PDF — низкий остаток")
        self.btn_pdf.clicked.connect(self._pdf)
        btn_layout.addWidget(self.btn_pdf)

        self.btn_excel = QtWidgets.QPushButton("Сохранить XLSX — просроченные")
        self.btn_excel.clicked.connect(self._excel)
        btn_layout.addWidget(self.btn_excel)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # Первичная загрузка
        self.reload()

    def showEvent(self, event):
        # Обновляем таблицы каждый раз при показе страницы
        self.reload()
        super().showEvent(event)

    def reload(self):
        # Обновляем низкий остаток
        low_books = controllers.find_books()
        self.tbl_low.setRowCount(0)
        for b in low_books:
            if b.copies < 2:
                r = self.tbl_low.rowCount()
                self.tbl_low.insertRow(r)
                for c, val in enumerate([b.id, b.title, b.author, b.copies]):
                    item = QtWidgets.QTableWidgetItem(str(val))
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.tbl_low.setItem(r, c, item)
        # Обновляем просроченные
        overdue_orders = controllers.list_all_orders()
        self.tbl_over.setRowCount(0)
        for o in overdue_orders:
            if o.status == 'overdue':
                r = self.tbl_over.rowCount()
                self.tbl_over.insertRow(r)
                issue_str = o.issue_date.strftime("%Y-%m-%d") if o.issue_date else ""
                for c, val in enumerate([o.id, o.user_id, o.book.title, o.status, issue_str]):
                    item = QtWidgets.QTableWidgetItem(str(val))
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.tbl_over.setItem(r, c, item)

    def _pdf(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Сохранить PDF", "", "PDF (*.pdf)"
        )
        if path:
            books = [b for b in controllers.find_books() if b.copies < 2]
            generate_low_stock_pdf(books, path)

    def _excel(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Сохранить XLSX", "", "Excel (*.xlsx)"
        )
        if path:
            orders = [o for o in controllers.list_all_orders() if o.status == 'overdue']
            generate_overdue_excel(orders, path)
