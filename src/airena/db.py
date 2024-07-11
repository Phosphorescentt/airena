import sqlite3
import json

from airena.enums import DatabaseSave
from airena.types import JsonType


def create_histories_table():
    con = sqlite3.connect("airena.db")
    con.execute(
        """create table if not exists histories(
            id integer primary key,
            adapters_json text not null,
            history_json text not null
        );"""
    )
    con.commit()


def write_history_to_db(
    adapters_json: JsonType, history_json: JsonType
) -> DatabaseSave:
    create_histories_table()

    con = sqlite3.connect("airena.db")
    con.execute(
        f"""insert into histories (adapters_json, history_json)
        values (?, ?)""",
        (json.dumps(adapters_json), json.dumps(history_json)),
    )
    con.commit()
    return DatabaseSave.SUCCESS
