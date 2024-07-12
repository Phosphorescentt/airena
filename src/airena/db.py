import sqlite3
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, List, Optional

from airena.enums import DatabaseSave
from airena.review import ReviewInformation

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


# TODO: Fix this scuffed datamoddel - this is not versatile in any way and
# this is just going to cause me problems later on :)
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
            score float,
            foreign key(conversation_history_id) references conversation_history(id)
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


def get_unreviewed_conversation_history() -> ReviewInformation:
    with get_db_connection() as con:
        cur = con.cursor()

        # Pick a conversation_id with unreviewed conversation_history records
        cur.execute(
            """
            select * from conversation_history as ch
            left join review as r on r.conversation_history_id = ch.id
            where r.score is null
            """
        )
        unreviewed_conversation_history_record = cur.fetchone()
        conversation_id = unreviewed_conversation_history_record[1]

        # Get all conversation_history records with conversation_id
        cur.execute(
            """
            select * from conversation_history as ch
            left join review as r on r.conversation_history_id = ch.id
            where ch.conversation_id = ?
            """,
            (conversation_id,),
        )
        history_points = cur.fetchall()
        history_points_ordered = sorted(history_points, key=lambda x: x[2])

        # Find ones without a score in review
        first_unreviewed_message: List[Any] = next(
            filter(lambda x: x[6] is None, history_points_ordered),
            None,  # type: ignore
        )
        first_unreviewed_message_number = first_unreviewed_message[2]
        last_unreviewed_message: Optional[List[Any]] = next(
            filter(
                lambda x: x[6] is not None,
                history_points_ordered[first_unreviewed_message_number:],
            ),
            None,
        )
        last_unreviewed_message_number = (
            last_unreviewed_message[2] if last_unreviewed_message else None
        )

        # Get total conversation participants.
        cur.execute(
            """
            select * from conversation_participant as cp
            where cp.conversation_id = ?
            """,
            (conversation_id,),
        )
        total_participants = len(cur.fetchall())

        # Get system prompt
        cur.execute(
            """
            select system_prompt from conversation where id = ?
            """,
            (conversation_id,),
        )
        system_prompt = cur.fetchone()[0]

        return ReviewInformation(
            conversation_id=conversation_id,
            total_participants=total_participants,
            first_message=first_unreviewed_message_number,
            last_message=last_unreviewed_message_number,
            system_prompt=system_prompt,
            history=[h[3] for h in history_points_ordered],
        )


def write_conversation_history_point_score(
    conversation_id: int, message_number: int, score: float
) -> DatabaseSave:
    with get_db_connection() as con:
        cur = con.cursor()

        # Find conversation_history_id
        cur.execute(
            """
            select id from conversation_history
            where conversation_id = ?
            and message_number = ?
            """,
            (conversation_id, message_number),
        )
        conversation_history_id = cur.fetchone()[0]

        # Insert score into review
        cur.execute(
            """
            insert into review(conversation_history_id, score)
            values (?, ?)
            """,
            (conversation_history_id, score),
        )
        con.commit()

    return DatabaseSave.SUCCESS
