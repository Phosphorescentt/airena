from peewee import SqliteDatabase
import pytest
from tempfile import NamedTemporaryFile

import airena.db as db


@pytest.fixture
def mock_database():
    with NamedTemporaryFile() as ntf:
        mock_db = SqliteDatabase(ntf.name)
        _mock_binds = [c.bind(mock_db) for c in db.BaseModel.__subclasses__()]
        db.setup_db(mock_db)
        yield
