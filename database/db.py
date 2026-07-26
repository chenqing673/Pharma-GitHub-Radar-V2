from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///data/pharma_radar.db"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine)


def get_session():
    return SessionLocal()


def init_db():
    from database.models import Base

    Base.metadata.create_all(bind=engine)
    _migrate_trending_columns()


def _migrate_trending_columns():
    """补齐 trending_repos 表可能缺失的新字段（兼容旧 db 文件）。"""
    from sqlalchemy import text

    needed = {
        "topics": "VARCHAR(300)",
        "zh_intro": "TEXT",
    }
    try:
        with engine.connect() as conn:
            cols = [
                row[1]
                for row in conn.execute(text("PRAGMA table_info(trending_repos)")).fetchall()
            ]
            for col, col_type in needed.items():
                if col not in cols:
                    conn.execute(
                        text(f"ALTER TABLE trending_repos ADD COLUMN {col} {col_type}")
                    )
            conn.commit()
    except Exception:
        # 表不存在等情况交给 create_all 处理，不阻断主流程
        pass
