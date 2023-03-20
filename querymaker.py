import sqlite3
from dataclasses import dataclass
from enum import Enum
from random import randint

# TODO: Docs


def con():
    return sqlite3.connect("data/spirit.db")


class Sort(Enum):
    NAME_DESC = 0
    NAME_ASC = 1
    POINTS_DESC = 2
    POINTS_ASC = 3

    def from_string(string):
        return {
            "name_desc": Sort.NAME_DESC,
            "name_asc": Sort.NAME_ASC,
            "points_desc": Sort.POINTS_DESC,
            "points_asc": Sort.POINTS_ASC,
        }.get(string, Sort.NAME_DESC)

    def to_query(sort):
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

    def to_json(self):
        return self.__dict__


# TODO: string query -> Query Object -> SQL string -> people
def get_students_matching(starting_with: str, limit=10):
    return [
        Student(*x)
        for x in con().execute(
            f"SELECT NAME,POINTS,GRADE FROM STUDENTS WHERE NAME LIKE ? LIMIT ?;",
            (
                f"%{starting_with}%",
                limit,
            ),
        )
    ]


def get_students(limit=50, sort=Sort.NAME_DESC):
    sq = Sort.to_query(sort)
    return [
        Student(*x)
        for x in con().execute(
            f"SELECT NAME,POINTS,GRADE FROM STUDENTS ORDER BY {sq} LIMIT ?;", (limit,)
        )
    ]


@dataclass
class Event:
    id: int
    name: str
    location: str
    desc: str

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "desc": self.desc,
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
    # TODO: Dates

    return [
        Event(*x)
        for x in con().execute(
            "SELECT ID,NAME,LOCATION,DESCRIPTION FROM EVENTS;",
        )
    ]


def get_random_student(grade: int) -> Student:
    dat = next(
        con().execute(
            "SELECT NAME,POINTS,GRADE FROM STUDENTS WHERE GRADE = ? AND POINTS > 0 ORDER BY RANDOM() LIMIT 1;",
            (grade,),
        )
    )
    return Student(*dat)

def get_prizes() -> list[Prize]:
    return [
        Prize(*x)
        for x in con().execute(
            "SELECT NAME,DESC,POINTS_REQUIRED FROM PRIZES;",
        )
    ]
