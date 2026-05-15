from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

# 根据数据库类型设置不同的连接参数
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # PostgreSQL 连接健康检查
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _sync_sequences(db_url: str):
    """PostgreSQL: 将自增序列同步到表中实际最大 ID，防止 UniqueViolation。"""
    if not db_url.startswith("postgresql"):
        return
    from app.models.user import User
    from app.models.product import Product
    from app.models.supplier import Supplier

    tables = [
        ("users_id_seq", User.__tablename__),
        ("products_id_seq", Product.__tablename__),
        ("suppliers_id_seq", Supplier.__tablename__),
    ]
    with engine.begin() as conn:
        for seq_name, table_name in tables:
            max_id = conn.execute(text(f"SELECT MAX(id) FROM {table_name}")).scalar()
            if max_id is None:
                max_id = 0
            conn.execute(text(f"SELECT setval('{seq_name}', :val)"), {"val": max(1, max_id)})


def init_db():
    from app.models import user, product, supplier  # noqa
    Base.metadata.create_all(bind=engine)
    _sync_sequences(settings.DATABASE_URL)
