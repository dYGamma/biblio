from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from openpyxl import Workbook

def generate_low_stock_pdf(books, filename: str):
    c = canvas.Canvas(filename, pagesize=A4)
    w,h = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, h-50, "Отчет: низкий остаток книг")
    c.setFont("Helvetica", 12)
    y = h-80
    for b in books:
        c.drawString(50, y, f"ID:{b.id} «{b.title}» — {b.author} [копий:{b.copies}]")
        y -= 20
        if y<50:
            c.showPage(); c.setFont("Helvetica",12); y=h-50
    c.save()

def generate_overdue_excel(orders, filename: str):
    wb = Workbook(); ws = wb.active; ws.title="Просроченные"
    ws.append(["ID заказа","ID ученика","Название","Статус","Дата выдачи"])
    for o in orders:
        ws.append([
            o.id, o.user_id, o.book.title,
            o.status.value,
            o.issue_date.strftime("%Y-%m-%d") if o.issue_date else ''
        ])
    wb.save(filename)
