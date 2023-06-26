from __future__ import annotations
from flask import session
import inspect
import json
import logging
import random
import sqlite3
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

GRADES = [9, 10, 11, 12]
VALID_INT_OPERANDS = ["<", "<=", ">", ">=", "="]
DATABASE_PATH = "data/spirit.db"
PRIZE_DB_PATH = "data/prizes.json"
DEBUG_DB_CALLS = False
MAXIMUM_COMMIT_RETRIES = 10
MAXIMUM_COMMIT_BACKOFF_SECONDS = 10

logger = logging.getLogger("spirit.database")


class Connection(sqlite3.Connection):
    def __init__(self) -> None:
        super().__init__(DATABASE_PATH)

    def nab(self, query: str, params: Optional[tuple] = None) -> Optional[list]:
        row = self.nab_row(query, params or tuple())
        if not row:
            return None
        return row[0]

    def nab_row(self, query: str, params: Optional[tuple] = None) -> Optional[list]:
        """Convienience wrapper

        Args:
            query (str): _description_
            params (Optional[tuple], optional): _description_. Defaults to None.

        Returns:
            Optional[list]: _description_
        """
        params = params or tuple()
        return self.execute(query, params).fetchone()

    def commit(self, *args, **kwargs):
        error_count = 0

        while True:
            try:
                # Return immediately upon success
                return super().commit(*args, **kwargs)
            except sqlite3.OperationalError as e:
                # Otherwise, increment error counter
                error_count += 1
                logger.error(f"Failed to commit on try {error_count}: {e}")

                # If we have too many retries, raise the error
                if error_count >= MAXIMUM_COMMIT_RETRIES:
                    logger.error("Reached maximum retry count. Raising error.")
                    raise

                # Exponential backoff: give competing threads a chance to commit
                time.sleep(
                    min(
                        # Exponent base chosen via messing around in graphing calculator,
                        # can be changed if appropriate. Random offset added to aid in
                        # desyncing if multiple retries are being attempted in tandem.
                        (1.3**error_count) + random.rand(),
                        # Don't wait for too long
                        MAXIMUM_COMMIT_BACKOFF_SECONDS,
                    )
                )


def con() -> Connection:
    """Shorthand wrapper for Connection() constructor with debug capabilities; use
    this rather than instantiating a Connection directly.

    Returns:
        Connection: A database connection object.
    """
    if DEBUG_DB_CALLS:
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        logger.debug("[ConCall]", calframe[1][3])
    return Connection()


def prize_dat() -> dict:
    """Convenience function for hot-loading prize data from the JSON file.

    Returns:
        dict: A dictionary of all the prizes in the prize file.
    """
    with open(PRIZE_DB_PATH, "r") as file:
        return json.load(file)


class Sort(Enum):
    """An enum representing database ORDER BY qualifiers."""

    NAME_DESC = 0
    NAME_ASC = 1
    POINTS_DESC = 2
    POINTS_ASC = 3

    @staticmethod
    def from_string(string: str) -> Sort:
        """Returns a Sort enum from a preset string. Intended for use in converting user input to a Sort type.

        Args:
            string (str): The string mapping to a sort value.

        Returns:
            Sort: The sort for the given string. Sort.NAME_DESC is returned if the string does not map to a Sort.
        """
        return {
            "name_desc": Sort.NAME_DESC,
            "name_asc": Sort.NAME_ASC,
            "points_desc": Sort.POINTS_DESC,
            "points_asc": Sort.POINTS_ASC,
        }.get(string, Sort.NAME_DESC)

    @staticmethod
    def to_query(sort: Sort) -> str:
        """Converts a passed Sort enum to an ORDER BY clause qualifier.

        Args:
            sort (Sort): The sort in question.

        Returns:
            str: Column and direction for ORDER BY clause.
        """
        return {
            Sort.NAME_DESC: "NAME DESC",
            Sort.NAME_ASC: "NAME ASC",
            Sort.POINTS_DESC: "POINTS DESC",
            Sort.POINTS_ASC: "POINTS ASC",
        }[sort]


@dataclass
class Student:
    """A representation of a student within the database."""

    name: str
    points: int
    grade: int
    id: int
    rank: int

    def __post_init__(self) -> None:
        self.points = int(self.points or 0)
        self.grade = int(self.grade or 9)
        self.id = int(self.id)
        self.rank = int(self.rank)

    @staticmethod
    def from_name(name: str) -> Student:
        """Returns a Student that has a given name.

        Args:
            name (str): The student's name.

        Returns:
            Student: The student with the given name.
        """
        return Student(
            *con().nab_row(
                "SELECT NAME,POINTS,GRADE,ROWID,STUDENT_RANK FROM USERS WHERE NAME = ?;", (name,)
            )
        )

    @staticmethod
    def random_from_grade(grade: int) -> Student:
        return Student(
            *con().nab_row(
                "SELECT NAME,POINTS,GRADE,ROWID,STUDENT_RANK FROM USERS WHERE GRADE = ? AND POINTS > 0 ORDER BY RANDOM() LIMIT 1;",
                (grade,),
            )
        )

    def to_json(self):
        return self.__dict__

    def get_score_rank(self) -> int:
        """Returns what place the student is in when the databse is ranked by points descending.

        Returns:
            int: Student's rank (place).
        """
        return con().nab(
            "WITH cte AS (SELECT id, RANK() OVER (ORDER BY points DESC) rnk FROM STUDENTS)"
            + "SELECT id, rnk FROM cte WHERE id = ?;",
            (self.id,),
        )


def get_students_matching(substring: str, limit=10) -> list[Student]:
    """Returns {limit} students whose names include {substring}.

    Args:
        substring (str): Substring to check name inclusion.
        limit (int, optional): Maximum amount of students to return. Defaults to 10.

    Returns:
        list[Student]: The students fetched by the operation.
    """
    return [
        Student(*x)
        for x in con().execute(
            f"SELECT NAME,POINTS,GRADE,ROWID,STUDENT_RANK FROM USERS WHERE NAME LIKE ?, SCHOOL_ID = ? LIMIT ?;",
            (
                f"%{substring}%",
                session["school_id"],
                limit,
            ),
        )
    ]


@dataclass
class WhereClause:
    """A structure representing a single component of a WHERE clause (which
    evaluates to a boolean)."""

    condition: str
    args: list


def get_students(
    limit: int = 50,
    sort: Sort = Sort.NAME_DESC,
    score_condition: str = ">0",
    query: Optional[str] = None,
    grade_filters: Optional[dict] = None,
) -> list[Student]:
    """A monolithic query function to fetch a list of students matching certain criteria.

    Args:
        limit (int, optional): Maximum amount of students to return. Defaults to 50.
        sort (Sort, optional): Query ORDER BY method. Defaults to Sort.NAME_DESC.
        score_condition (str, optional): A string representing a numerical constraint
            on the score value. Defaults to ">0".
        query (Optional[str], optional): A substring to match names to. Defaults to None.
        grade_filters (Optional[dict], optional): A dict determining which grades
            should be allowed/disallowed from the results. Defaults to None.

    Raises:
        ValueError: Unexpected user input made it past other filters. This should
            not be handled by the caller; instead the caller should process the
            user input appropriately.

    Returns:
        list[Student]: The students returned satisfying the constraints of the query.
    """

    grade_filters = grade_filters or {}
    sq = Sort.to_query(sort)
    where_clauses = []

    if query:
        where_clauses.append(WhereClause(condition="NAME LIKE ?", args=[f"%{query}%"]))

    for grade, allow in grade_filters.items():
        if allow:
            continue

        where_clauses.append(WhereClause(condition="GRADE != ?", args=[grade]))

    if score_condition:
        score_operand = score_condition[0]
        # Don't want sql injection! All text inserted directly into the
        # query must be super duper squeaky clean.
        if score_operand not in VALID_INT_OPERANDS:
            raise ValueError("Evil operand!")

        try:
            score_value = int(score_condition[1:])
        except ValueError:
            # Score is not an int! Possible SQL injection attempt!
            raise

        where_clauses.append(
            WhereClause(condition=f"POINTS {score_operand} ?", args=[score_value])
        )
    where_clauses.append(
        WhereClause(condition=f"SCHOOL_ID = ?", args=[session["school_id"]])
    )
    where_clauses.append(WhereClause(condition=f"ROLE = ?", args=["STUDENT"]))
    where_clause = ""
    where_args = []
    if where_clauses:
        where_clause = "WHERE " + (" AND ".join([x.condition for x in where_clauses]))
        for clause in where_clauses:
            where_args += clause.args

    return [
        Student(*x)
        for x in con().execute(
            f"SELECT NAME,POINTS,GRADE,ROWID,STUDENT_RANK FROM USERS {where_clause} ORDER BY {sq} LIMIT ?;",
            (
                *where_args,
                limit,
            ),
        )
    ]


@dataclass
class Event:
    """A representation of an event within the database."""

    id: int
    name: str
    location: str
    desc: str
    points: int
    time_start: int
    time_end: int

    @staticmethod
    def from_id(event_id: int) -> Event:
        return Event(
            *con().nab_row(
                "SELECT ID,NAME,LOCATION,DESCRIPTION,POINTS,TIME_START,TIME_END FROM EVENTS WHERE ID = ?;",
                (event_id,),
            )
        )

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "desc": self.desc,
            "points": self.points,
            "time_start": self.time_start,
            "time_end": self.time_end,
        }

    def set_student_interest(self, student_id: int, interested: bool) -> None:
        """Marks or unmarks the given student as interested in the event.

        Args:
            student_id (int): The ID of the student in question.
            interested (bool): Whether or not the student is interested in attending.
        """
        connection = con()
        if interested:
            connection.execute(
                "INSERT INTO STUDENT_ATTENDANCE_INTENT(STUDENT_ID, EVENT_ID) VALUES(?, ?);",
                (student_id, self.id),
            )
        else:
            connection.execute(
                "DELETE FROM STUDENT_ATTENDANCE_INTENT WHERE STUDENT_ID = ? AND EVENT_ID = ?;",
                (student_id, self.id),
            )
        connection.commit()

    def get_student_interest(self, student_id: int) -> bool:
        """Returns if a given student is interested in the event.

        Args:
            student_id (int): The ID of the student in question.

        Returns:
            bool: Whether or not the student is interested in attending.
        """
        return bool(
            con().nab(
                "SELECT 1 FROM STUDENT_ATTENDANCE_INTENT WHERE STUDENT_ID = ? AND EVENT_ID = ?;",
                (student_id, self.id),
            )
        )

    def get_aggregate_student_interest(self) -> int:
        """Returns the count of students interested in attending the event.

        Returns:
            int: The amount of students interested in attending.
        """
        return con().nab(
            "SELECT COUNT() FROM STUDENT_ATTENDANCE_INTENT WHERE EVENT_ID = ?;",
            (self.id,),
        )


@dataclass
class Prize:
    name: str
    desc: str
    points_required: int

    def __post_init__(self) -> None:
        self.points_required = int(self.points_required)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "desc": self.desc,
            "points_required": self.points_required,
        }


def get_upcoming_events() -> list[Event]:
    return [
        Event(*x)
        for x in con().execute(
            "SELECT ID,NAME,LOCATION,DESCRIPTION,POINTS,TIME_START,TIME_END FROM EVENTS;",
        )
    ]


def get_prizes() -> list[Prize]:
    return [Prize(**x) for x in prize_dat()]


def get_aggregate_stats() -> dict:
    stats = {
        "points_by_grade": {},
        "attendance_ratio_by_grade": {},
        "avg_attendances_by_grade": {},
    }

    for grade in GRADES:
        stats["points_by_grade"][grade] = next(
            con().execute(
                "SELECT SUM(POINTS) FROM USERS WHERE GRADE = ?;",
                (grade,),
            )
        )[0]

        stats["attendance_ratio_by_grade"][grade] = next(
            con().execute(
                "SELECT (SELECT COUNT() FROM USERS WHERE GRADE = ? AND POINTS > 0) * 1.0 / (SELECT COUNT() FROM USERS WHERE GRADE = ?) * 1.0;",
                (grade, grade),
            )
        )[0]

        stats["avg_attendances_by_grade"][grade] = next(
            con().execute(
                "SELECT (SELECT COUNT() FROM STUDENT_ATTENDANCE WHERE STUDENT_ID IN (SELECT ID FROM USERS WHERE GRADE = ?)) * 1.0 / (SELECT COUNT() FROM USERS WHERE GRADE = ?) * 1.0;",
                (grade, grade),
            )
        )[0]

    return stats


def reindex_scores() -> None:
    logger.debug("[db] Indexing scores...")
    with con() as c:
        c.execute(
            """UPDATE USERS SET POINTS = (SELECT SUM(EVENTS.POINTS) FROM EVENTS WHERE EVENTS.ID IN (SELECT EVENT_ID FROM STUDENT_ATTENDANCE WHERE STUDENT_ID = USERS.ID)) + SURPLUS;"""
        )
        c.execute("UPDATE USERS SET POINTS = SURPLUS WHERE POINTS IS NULL;")
        c.execute(
            "UPDATE USERS SET STUDENT_RANK = R FROM (SELECT ID, DENSE_RANK() OVER(ORDER BY POINTS DESC) R FROM USERS WHERE SCHOOL_ID = ? AND ROLE = 'STUDENT') X WHERE USERS.ID = X.ID",
            (session["school_id"],),
        )
        c.commit()
    logger.debug("[db] Done!")


@dataclass
class Request:
    operation: str
    name: str
    email: str
    grade: int
    role: str
    id: int

    def to_json(self) -> dict:
        return self.__dict__


def get_mail(username):
    with con() as c:
        return [
            Request(*x)
            for x in c.execute(
                f"SELECT OPERATION, NAME, EMAIL, GRADE, ROLE, ROWID FROM REQUESTS WHERE SCHOOL_ID = (SELECT SCHOOL_ID FROM USERS WHERE NAME = ?);",
                (username,),
            )
        ]


# Reindex scores on startup to ensure database integrity after
# potential edits outside the application.
