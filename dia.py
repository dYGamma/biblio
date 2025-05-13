from graphviz import Digraph

# создаём объект диаграммы
dot = Digraph('ER_Diagram', format='png')
dot.attr(rankdir='LR', fontsize='12')

# определяем узлы (таблицы) и их поля
dot.node('users', '''<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">
  <TR><TD COLSPAN="2"><B>users</B></TD></TR>
  <TR><TD><I>id PK</I></TD><TD>varchar</TD></TR>
  <TR><TD>name</TD><TD>varchar</TD></TR>
  <TR><TD>role</TD><TD>varchar</TD></TR>
  <TR><TD>clazz</TD><TD>int</TD></TR>
  <TR><TD>contact</TD><TD>varchar</TD></TR>
  <TR><TD>password_hash</TD><TD>varchar</TD></TR>
</TABLE>>''')

dot.node('books', '''<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">
  <TR><TD COLSPAN="2"><B>books</B></TD></TR>
  <TR><TD><I>id PK</I></TD><TD>int</TD></TR>
  <TR><TD>isbn</TD><TD>varchar</TD></TR>
  <TR><TD>title</TD><TD>varchar</TD></TR>
  <TR><TD>author</TD><TD>varchar</TD></TR>
  <TR><TD>genre</TD><TD>varchar</TD></TR>
  <TR><TD>year</TD><TD>int</TD></TR>
  <TR><TD>copies</TD><TD>int</TD></TR>
  <TR><TD>description</TD><TD>text</TD></TR>
  <TR><TD>added_at</TD><TD>datetime</TD></TR>
</TABLE>>''')

dot.node('orders', '''<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">
  <TR><TD COLSPAN="2"><B>orders</B></TD></TR>
  <TR><TD><I>id PK</I></TD><TD>int</TD></TR>
  <TR><TD><I>user_id FK</I></TD><TD>varchar</TD></TR>
  <TR><TD><I>book_id FK</I></TD><TD>int</TD></TR>
  <TR><TD>status</TD><TD>varchar</TD></TR>
  <TR><TD>request_date</TD><TD>datetime</TD></TR>
  <TR><TD>confirm_date</TD><TD>datetime</TD></TR>
  <TR><TD>issue_date</TD><TD>datetime</TD></TR>
  <TR><TD>return_date</TD><TD>datetime</TD></TR>
  <TR><TD>due_date</TD><TD>datetime</TD></TR>
</TABLE>>''')

# связи
dot.edge('users', 'orders', label='1 — N', tailport='e', headport='w')
dot.edge('books', 'orders', label='1 — N', tailport='e', headport='w')

# сохраняем и (при поддержке) отображаем
output_path = dot.render('er_diagram')
print(f"ER‑диаграмма сохранена в {output_path}")
