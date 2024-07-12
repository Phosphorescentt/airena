import sqlite3
from contextlib import contextmanager
from typing import TYPE_CHECKING, Optional

from airena.enums import DatabaseSave

if TYPE_CHECKING:
    from airena.engine import DebateEngine


DB_FILENAME = "airena.db"


@contextmanager
def get_db_connection():
    con = sqlite3.connect(DB_FILENAME)
    try:
        yield sqlite3.connect(DB_FILENAME)
    finally:
        con.close()


# TODO: Upgrade this to SQLAlchemy + alembic or something. cba with managing this
# long term but this works for now.
def setup_db(con: Optional[sqlite3.Connection] = None):
    with get_db_connection() as con:
        create_conversation_table(con)
        create_conversation_participant_table(con)
        create_conversation_history_table(con)
        create_review_table(con)
        con.commit()


def create_conversation_table(con: sqlite3.Connection):
    con.execute(
        """
        create table if not exists conversation(
            id integer primary key,
            total_participants integer,
            length integer,
            system_prompt text
        );
        """
    )


def create_conversation_participant_table(con: sqlite3.Connection):
    con.execute(
        """
        create table if not exists conversation_participant(
            id integer primary key,
            model_name text,
            turn_position integer,
            conversation_id integer,
            foreign key(conversation_id) references conversation(id)
        );
        """
    )


def create_conversation_history_table(con: sqlite3.Connection):
    con.execute(
        """
        create table if not exists conversation_history(
            id integer primary key,
            conversation_id integer,
            message_number integer,
            message_content text,
            foreign key(conversation_id) references conversation(id)
        );
        """
    )


def create_review_table(con: sqlite3.Connection):
    con.execute(
        """
        create table if not exists review(
            id integer primary key,
            conversation_history_id integer,
            participant_id integer,
            score integer,
            foreign key(conversation_history_id) references conversation_history(id),
            foreign key(participant_id) references conversation_participant(id)
        );
        """
    )


def write_history(engine: "DebateEngine") -> DatabaseSave:
    with get_db_connection() as con:
        cur = con.cursor()

        # Create conversation
        cur.execute(
            """
            insert into conversation(total_participants, length, system_prompt)
            values (?, ?, ?)
            """,
            (
                len(engine.adapters),
                engine.max_conversation_depth,
                engine.history.system_prompt,
            ),
        )
        conversation_id = cur.lastrowid
        con.commit()

        # Create participants
        adapter_participant_id_map = {}
        for adapter in engine.adapters:
            cur.execute(
                """
                insert into
                conversation_participant(model_name, turn_position, conversation_id)
                values (?, ?, ?)
                """,
                (
                    adapter.model_name,
                    adapter._turn_information.position,
                    conversation_id,
                ),
            )
            participant_id = cur.lastrowid
            adapter_participant_id_map[adapter] = participant_id
            con.commit()

        # Crteate conversation histories
        for i, row in enumerate(engine.history.rows):
            cur.execute(
                """
                insert into
                conversation_history(message_number, message_content, conversation_id)
                values (?, ?, ?)
                """,
                (i, row, conversation_id),
            )
            con.commit()

    return DatabaseSave.SUCCESS


def get_unreviewed_conversation_history_point():
    with get_db_connection() as con:
        con.execute(
            """
            select * from conversation_history as ch
            join review as r on r.conversation_history_id = ch.id
            where r.score = null
            """
        )


def write_conversation_history_point_score():
    con = get_db_connection()
