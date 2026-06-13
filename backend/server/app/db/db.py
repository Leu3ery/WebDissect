from contextlib import contextmanager
from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session

from app.db.models._base import Base
from app.config import get_settings


# --- domain-level DB exceptions ------------------------------------------
class DBError(Exception):
    """Base for any DB failure surfaced past the handler boundary."""

class DBIntegrityError(DBError):
    """Constraint violation: duplicate key, NOT NULL, FK, ..."""

class DBConnectionError(DBError):
    """Operational failure: db unreachable, locked, ..."""


class DBHandler:
    def __init__(self, url: str | None = None):
        self.engine = create_engine(
            url or ("sqlite:////app/db/" + get_settings().DB_FILENAME),
            pool_pre_ping=True,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def init_db(self) -> None:
        Base.metadata.create_all(self.engine)


    @contextmanager
    def transaction(self) -> Iterator[Session]:
        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise DBIntegrityError(str(e.orig)) from e
        except OperationalError as e:
            db.rollback()
            raise DBConnectionError(str(e.orig)) from e
        except SQLAlchemyError as e:
            db.rollback()
            raise DBError(str(e)) from e
        except Exception:          # non-DB error raised inside the block
            db.rollback()          # still roll back, but don't translate to custom error
            raise
        finally:
            db.close()

db_handler = DBHandler()

