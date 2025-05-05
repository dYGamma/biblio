from PyQt5 import QtWidgets

class BookDialog(QtWidgets.QDialog):
    def __init__(self, book=None):
        super().__init__()
        self.setWindowTitle("Книга")
        self.le_isbn = QtWidgets.QLineEdit()
        self.le_title = QtWidgets.QLineEdit()
        self.le_author= QtWidgets.QLineEdit()
        self.le_genre = QtWidgets.QLineEdit()
        self.sb_year  = QtWidgets.QSpinBox(); self.sb_year.setRange(0, 3000)
        self.sb_copies= QtWidgets.QSpinBox(); self.sb_copies.setRange(0, 1000)
        self.te_desc  = QtWidgets.QTextEdit()
        form = QtWidgets.QFormLayout(self)
        form.addRow("ISBN:", self.le_isbn)
        form.addRow("Название:", self.le_title)
        form.addRow("Автор:", self.le_author)
        form.addRow("Жанр:", self.le_genre)
        form.addRow("Год:", self.sb_year)
        form.addRow("Копий:", self.sb_copies)
        form.addRow("Описание:", self.te_desc)
        btn = QtWidgets.QPushButton("OK")
        btn.clicked.connect(self.accept)
        form.addRow(btn)

        if book:
            self.le_isbn.setText(book.isbn or '')
            self.le_title.setText(book.title)
            self.le_author.setText(book.author)
            self.le_genre.setText(book.genre or '')
            self.sb_year.setValue(book.year or 0)
            self.sb_copies.setValue(book.copies)
            self.te_desc.setPlainText(book.description or '')

    def get_data(self):
        return {
            'isbn': self.le_isbn.text().strip() or None,
            'title':self.le_title.text().strip(),
            'author':self.le_author.text().strip(),
            'genre':self.le_genre.text().strip() or None,
            'year': self.sb_year.value() or None,
            'copies': self.sb_copies.value(),
            'description': self.te_desc.toPlainText().strip() or None
        }
