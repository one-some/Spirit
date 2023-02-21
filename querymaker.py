import sqlite3
from dataclasses import dataclass
from enum import Enum
from random import randint

def con():
    return sqlite3.connect("data.db")

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
    grade: int = None

    def __post_init__(self) -> None:
        # TODO: THIS IS A HACK
        self.grade = randint(9, 12)
    
    def to_json(self):
        return self.__dict__



# TODO: string query -> Query Object -> SQL string -> people
def get_students_matching(starting_with: str, limit=10):
    return [
        Student(*x)
        for x in con().execute(
            f"SELECT NAME,POINTS FROM STUDENTS WHERE NAME LIKE ? LIMIT ?;",
            (f"%{starting_with}%", limit,)
        )
    ]

def get_students(limit=50, sort=Sort.NAME_DESC):
    sq = Sort.to_query(sort)
    return [
        Student(*x)
        for x in con().execute(
            f"SELECT NAME,POINTS FROM STUDENTS ORDER BY {sq} LIMIT ?;",
            (limit,)
        )
    ]
