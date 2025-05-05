# controllers.py

import enum
import logging
from types import SimpleNamespace
from datetime import datetime, date, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound
from database import SessionLocal
from models import User, Book, Order, RoleEnum, StatusEnum
import reports
from plyer import notification

logger = logging.getLogger(__name__)

def _to_ns(obj, fields):
    data = {}
    for f in fields:
        val = getattr(obj, f)
        data[f] = val.value if isinstance(val, enum.Enum) else val
    return SimpleNamespace(**data)

# --- Authentication ---
def authenticate(user_id: str, password: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.verify_password(password):
            return user.role.value
    finally:
        db.close()
    return None

def get_user(user_id: str):
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.id == user_id).one()
        return SimpleNamespace(
            id=u.id, name=u.name, role=u.role.value,
            clazz=u.clazz, contact=u.contact
        )
    except NoResultFound:
        return None
    finally:
        db.close()

# --- User CRUD ---
def create_user(id: str, name: str, role: str, clazz: str=None, contact: str=None, password: str=None):
    db = SessionLocal()
    try:
        u = User(
            id=id,
            name=name,
            role=RoleEnum(role),
            clazz=clazz,
            contact=contact,
            password_hash=User.hash_password(password or '')
        )
        db.add(u)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    finally:
        db.close()

def update_user(id: str, **data):
    db = SessionLocal()
    try:
        u = db.get(User, id)
        for k,v in data.items():
            if k == 'password':
                setattr(u, 'password_hash', User.hash_password(v))
            else:
                setattr(u, k, v)
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

def delete_user(id: str):
    db = SessionLocal()
    try:
        db.query(User).filter(User.id == id).delete()
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

def list_users(role: str=None):
    db = SessionLocal()
    try:
        q = db.query(User)
        if role:
            q = q.filter(User.role == RoleEnum(role))
        return [
            SimpleNamespace(
                id=u.id,
                name=u.name,
                role=u.role.value,
                clazz=u.clazz,
                contact=u.contact
            )
            for u in q.all()
        ]
    finally:
        db.close()

def get_user_obj(id: str):
    return get_user(id)

# --- Book CRUD ---
def create_book(data: dict):
    db = SessionLocal()
    try:
        b = Book(**data)
        db.add(b)
        db.commit()
    finally:
        db.close()

def update_book(book_id: int, data: dict):
    db = SessionLocal()
    try:
        b = db.get(Book, book_id)
        for k,v in data.items():
            setattr(b, k, v)
        db.commit()
    finally:
        db.close()

def delete_book(book_id: int):
    db = SessionLocal()
    try:
        db.query(Book).filter(Book.id == book_id).delete()
        db.commit()
    finally:
        db.close()

def find_books():
    db = SessionLocal()
    try:
        return db.query(Book).all()
    finally:
        db.close()

def get_book(book_id: int):
    db = SessionLocal()
    try:
        b = db.get(Book, book_id)
        return _to_ns(b, ['id','isbn','title','author','genre','year','copies','description'])
    finally:
        db.close()

# --- Orders ---
def create_order(user_id: str, book_id: int):
    """
    Теперь сохраняем только дату заявки (без времени),
    чтобы в любом часовом поясе она совпадала с днём заказа.
    """
    db = SessionLocal()
    try:
        book = db.get(Book, book_id)
        if not book or book.copies < 1:
            raise Exception("Нет доступных копий для заказа.")
        cnt = db.query(Order).filter(
            Order.user_id==user_id,
            Order.status.in_([StatusEnum.pending, StatusEnum.confirmed, StatusEnum.issued])
        ).count()
        if cnt >= 3:
            raise Exception("Достигнут лимит одновременно взятых книг (3).")
        # создаём заказ и резервируем копию
        o = Order(
            user_id=user_id,
            book_id=book_id,
            request_date=date.today(),   # Здесь фиксируем лишь дату
            status=StatusEnum.pending
        )
        db.add(o)
        book.copies -= 1
        db.commit()
    except IntegrityError as e:
        db.rollback()
        logger.error("create_order failed: %s", e)
        raise
    finally:
        db.close()

def list_orders_for_user(user_id: str):
    db = SessionLocal()
    try:
        orders = db.query(Order).options(joinedload(Order.book))\
            .filter(Order.user_id==user_id).all()
        out = []
        for o in orders:
            ns = _to_ns(o, [
                'id','user_id','book_id','status',
                'request_date','confirm_date','issue_date','return_date','due_date'
            ])
            ns.book = SimpleNamespace(
                id=o.book.id if o.book else None,
                title=o.book.title if o.book else "[удалена]",
                author=o.book.author if o.book else ""
            )
            out.append(ns)
        return out
    finally:
        db.close()

def list_all_orders():
    db = SessionLocal()
    try:
        orders = db.query(Order).options(joinedload(Order.book)).all()
        result = []
        for o in orders:
            ns = _to_ns(o, [
                'id','user_id','book_id','status',
                'request_date','confirm_date','issue_date','return_date','due_date'
            ])
            ns.book = SimpleNamespace(
                id=o.book.id if o.book else None,
                title=o.book.title if o.book else "[удалена]",
                author=o.book.author if o.book else ""
            )
            result.append(ns)
        return result
    finally:
        db.close()

def return_order(order_id: int):
    process_order(order_id, 'returned')

def advance_order(order_id: int):
    mapping = {'pending':'confirmed','confirmed':'issued','issued':'returned'}
    db = SessionLocal()
    try:
        o = db.get(Order, order_id)
        if o and o.status.value in mapping:
            process_order(order_id, mapping[o.status.value])
    finally:
        db.close()

def process_order(order_id: int, new_status: str):
    db = SessionLocal()
    try:
        o = db.get(Order, order_id)
        now = datetime.utcnow()
        o.status = StatusEnum(new_status)
        if new_status == 'confirmed':
            o.confirm_date = now
            notification.notify(title="Бронь подтверждена",
                                message=f"Ваш заказ #{o.id} подтверждён")
        elif new_status == 'issued':
            o.issue_date = now
            notification.notify(title="Книга выдана",
                                message=f"Вам выдана «{o.book.title}»")
        elif new_status == 'returned':
            o.return_date = now
            _change_copies(db, o.book_id, +1)
            notification.notify(title="Книга возвращена",
                                message=f"Вы вернули «{o.book.title}»")
        elif new_status == 'overdue':
            notification.notify(title="Просрочка",
                                message=f"Заказ #{o.id} просрочен")
        db.commit()
    finally:
        db.close()

def _change_copies(db, book_id: int, delta: int):
    b = db.get(Book, book_id)
    b.copies += delta

def set_due_date(order_id: int, due_date: datetime):
    db = SessionLocal()
    try:
        o = db.get(Order, order_id)
        if o.status not in [StatusEnum.confirmed, StatusEnum.issued]:
            raise Exception("Срок можно задать только для подтверждённых или выданных заказов.")
        o.due_date = due_date
        db.commit()
    finally:
        db.close()

def set_confirm_date(order_id: int, confirm_date: datetime):
    db = SessionLocal()
    try:
        o = db.get(Order, order_id)
        if not o:
            raise Exception("Заказ не найден.")
        o.confirm_date = confirm_date
        db.commit()
    finally:
        db.close()

def set_issue_date(order_id: int, issue_date: datetime):
    db = SessionLocal()
    try:
        o = db.get(Order, order_id)
        if not o:
            raise Exception("Заказ не найден.")
        o.issue_date = issue_date
        db.commit()
    finally:
        db.close()

# --- Reports ---
def export_low_stock_pdf(path: str):
    db = SessionLocal()
    try:
        low = db.query(Book).filter(Book.copies < 2).all()
        reports.generate_low_stock_pdf(low, path)
    finally:
        db.close()

def export_overdue_excel(path: str):
    db = SessionLocal()
    try:
        ov = db.query(Order).filter(Order.status == StatusEnum.overdue).all()
        reports.generate_overdue_excel(ov, path)
    finally:
        db.close()
