import json
import sqlite3
from dataclasses import dataclass
from enum import Enum

GRADES = [9, 10, 11, 12]


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
            "SELECT NAME,POINTS,GRADE FROM STUDENTS WHERE GRADE = ? AND POINTS > 0 ORDER BY RANDOM() LIMIT 1;",
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
                "SELECT SUM(POINTS) FROM STUDENTS WHERE GRADE = ?;",
                (grade,),
            )
        )

        stats["attendance_ratio_by_grade"][grade] = next(
            con().execute(
                "SELECT (SELECT COUNT() FROM STUDENTS WHERE GRADE = ? AND POINTS > 0) * 1.0 / (SELECT COUNT() FROM STUDENTS WHERE GRADE = ?) * 1.0;",
                (grade, grade),
            )
        )

        stats["avg_attendances_by_grade"][grade] = next(
            con().execute(
                "SELECT (SELECT COUNT() FROM STUDENT_ATTENDANCE WHERE STUDENT_ID IN (SELECT ID FROM STUDENTS WHERE GRADE = ?)) * 1.0 / (SELECT COUNT() FROM STUDENTS WHERE GRADE = ?) * 1.0;",
                (grade, grade),
            )
        )

    return stats


def reindex_scores():
    print("[db] Indexing scores...")
    c = con()
    c.execute(
        "UPDATE STUDENTS SET POINTS = (SELECT SUM(EVENTS.POINTS) FROM EVENTS WHERE EVENTS.ID IN (SELECT EVENT_ID FROM STUDENT_ATTENDANCE WHERE STUDENT_ID = STUDENTS.ID));"
    )
    c.commit()
    print("[db] Done!")


reindex_scores()
