import os
from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

cfg = ConfigParser()
cfg.read(os.path.join('config', 'config.ini'))
db_url = os.getenv('DATABASE_URL') or cfg.get('database', 'url')

if db_url.startswith('sqlite:///'):
    file_path = db_url.replace('sqlite:///', '', 1)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if db_url.startswith('sqlite') else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Создаёт таблицы и администраторов."""
    from models import User, RoleEnum

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # # admin
        # if not db.query(User).filter(User.id=='admin').first():
        #     db.add(User(
        #         id='admin', name='System Admin',
        #         role=RoleEnum.admin,
        #         password_hash=User.hash_password('admin')
        #     ))
        # librarian
        if not db.query(User).filter(User.id=='librarian').first():
            db.add(User(
                id='librarian', name='Default Librarian',
                role=RoleEnum.librarian,
                password_hash=User.hash_password('lib')
            ))
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
