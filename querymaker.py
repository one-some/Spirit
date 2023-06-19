from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Optional

GRADES = [9, 10, 11, 12]
VALID_INT_OPERANDS = ["<", "<=", ">", ">=", "="]


def con():
    return sqlite3.connect("data/spirit.db")


def prize_dat():
    with open("data/prizes.json", "r") as file:
        return json.load(file)


class Sort(Enum):
    NAME_DESC = 0
    NAME_ASC = 1
    POINTS_DESC = 2
    POINTS_ASC = 3

    @staticmethod
    def from_string(string: str):
        return {
            "name_desc": Sort.NAME_DESC,
            "name_asc": Sort.NAME_ASC,
            "points_desc": Sort.POINTS_DESC,
            "points_asc": Sort.POINTS_ASC,
        }.get(string, Sort.NAME_DESC)

    @staticmethod
    def to_query(sort: Sort):
        return {
            Sort.NAME_DESC: "NAME DESC",
            Sort.NAME_ASC: "NAME ASC",
            Sort.POINTS_DESC: "POINTS DESC",
            Sort.POINTS_ASC: "POINTS ASC",
        }[sort]


@dataclass
class Student:
    name: str
    points: int
    grade: int
    id: int

    def to_json(self):
        return self.__dict__


# TODO: string query -> Query Object -> SQL string -> people
def get_students_matching(starting_with: str, limit=10):
    return [
        Student(*x)
        for x in con().execute(
            f"SELECT NAME,POINTS,GRADE,ROWID FROM USERS WHERE NAME LIKE ? LIMIT ?;",
            (
                f"%{starting_with}%",
                limit,
            ),
        )
    ]


@dataclass
class WhereClause:
    condition: str
    args: list


def get_students(
    limit: int = 50,
    sort: Sort = Sort.NAME_DESC,
    score_condition: str = ">0",
    # Unused
    rank_condition: str = "",
    query: Optional[str] = None,
    grade_filters: Optional[dict] = None,
):
    # HACK: work around mutable type blehhhhing in non-default args
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

    where_clause = ""
    where_args = []
    if where_clauses:
        where_clause = "WHERE " + (" AND ".join([x.condition for x in where_clauses]))
        for clause in where_clauses:
            where_args += clause.args

    return [
        Student(*x)
        for x in con().execute(
            f"SELECT NAME,POINTS,GRADE,ROWID FROM USERS {where_clause} ORDER BY {sq} LIMIT ?;",
            (
                *where_args,
                limit,
            ),
        )
    ]


@dataclass
class Event:
    id: int
    name: str
    location: str
    desc: str
    points: int
    time_start: int
    time_end: int

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


@dataclass
class Prize:
    name: str
    desc: str
    points_required: int

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "desc": self.desc,
            "points_required": self.points_required,
        }


def get_event(event_id: int) -> Event:
    return Event(
        *next(
            con().execute(
                "SELECT ID,NAME,LOCATION,DESCRIPTION FROM EVENTS WHERE ID = ?;",
                (event_id,),
            )
        )
    )


def get_upcoming_events() -> list[Event]:
    return [
        Event(*x)
        for x in con().execute(
            "SELECT ID,NAME,LOCATION,DESCRIPTION,POINTS,TIME_START,TIME_END FROM EVENTS;",
        )
    ]


def get_random_student(grade: int) -> Student:
    dat = next(
        con().execute(
            "SELECT NAME,POINTS,GRADE,ROWID FROM USERS WHERE GRADE = ? AND POINTS > 0 ORDER BY RANDOM() LIMIT 1;",
            (grade,),
        )
    )
    return Student(*dat)


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


def reindex_scores():
    print("[db] Indexing scores...")
    c = con()
    c.execute(
        """UPDATE USERS SET POINTS = (SELECT SUM(EVENTS.POINTS) FROM EVENTS WHERE EVENTS.ID IN (SELECT EVENT_ID FROM STUDENT_ATTENDANCE WHERE STUDENT_ID = USERS.ID)) + SURPLUS;"""
    )
    c.execute("UPDATE USERS SET POINTS = SURPLUS WHERE POINTS IS NULL;")
    c.commit()
    print("[db] Done!")

def get_mail(username):
    c = con()
    return c.execute(f"SELECT OPERATION, NAME, EMAIL, PASSWORD, ROLE FROM REQUESTS WHERE SCHOOL_ID = (SELECT SCHOOL_ID FROM USERS WHERE NAME = '{username}')").fetchall()
reindex_scores()
