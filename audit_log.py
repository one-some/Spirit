import json
import os
import random
import sqlite3
from typing import Optional

import querymaker

ALPHABET = "abcdefghijklmnopqrstuvwxyz-0123456789"
ROLLBACK_ID_LENGTH = 8
ROLLBACK_DIR = "backup/restore_points"


def get_rollback_id() -> str:
    """Gets a unique 8 digit identifier string for storing rollback db copies.

    Returns:
        str: The rollback ID generated
    """
    rollback_id = None
    while (not rollback_id) or os.path.exists(
        os.path.join(ROLLBACK_DIR, rollback_id + ".db")
    ):
        rollback_id = "".join(random.sample(ALPHABET, ROLLBACK_ID_LENGTH))
    return rollback_id


def to_str(object) -> str:
    if type(object) in [
        querymaker.Student,
        querymaker.Event,
        querymaker.Prize,
    ]:
        return object.name

    return json.dumps(object.__dict__)


def report_event(
    user_name: str,
    action: str,
    details: Optional[dict] = None,
    allow_rollback: bool = False,
) -> None:
    """Reports events to the audit log database, where they can be viewed by
    the user in the web app at a later time. Must be called BEFORE any database
    action is made.

    Args:
        user_name (str): The name of the user performing the action
        action (str): The action being performed
        details (Optional[dict], optional): Dict of action details. Defaults to None.
        allow_rollback (bool, optional): If a backup is made to allow for rollbacks later. Defaults to False.
    """
    details = details or {}
    con = querymaker.con()

    rollback_id = None
    if allow_rollback:
        rollback_id = get_rollback_id()
        with sqlite3.connect(
            os.path.join(ROLLBACK_DIR, rollback_id + ".db")
        ) as rollback_db:
            con.backup(rollback_db)

    con.execute(
        "INSERT INTO audit_log(time, user, action, details, rollback_id) VALUES(STRFTIME('%s'), ?, ?, ?, ?)",
        (
            user_name,
            action,
            json.dumps(details, default=to_str) if details else None,
            rollback_id,
        ),
    )
    con.commit()
    con.close()
