import random
import sqlite3

STUDENT_COUNT = 1629
con = sqlite3.connect("data/spirit.db")
cur = con.cursor()

if (
    input(
        "This will wipe the database and populate it with random placeholder data. Please type 'okie dokie' to continue."
    )
    != "okie dokie"
):
    print("Goodbye. :^)")
    exit(1)
    raise RuntimeError

with open("data/first-names.txt", "r") as file:
    first_names = file.read().split("\n")

with open("data/names.txt", "r") as file:
    last_names = file.read().split("\n")

events = []

for row in con.execute("SELECT ID,POINTS FROM EVENTS;").fetchall():
    events.append({"id": row[0], "points": row[1]})

# WIPE
con.execute("DELETE FROM STUDENTS;")
con.execute("DELETE FROM STUDENT_ATTENDANCE;")


def get_name():
    return " ".join([random.choice(first_names), random.choice(last_names)])


grade_thresh = {
    9: random.randrange(0, 4),
    10: random.randrange(0, 4),
    11: random.randrange(0, 4),
    12: random.randrange(0, 4),
}

for _ in range(STUDENT_COUNT):
    name = get_name()
    grade = random.randint(9, 12)

    cur.execute(
        "INSERT INTO STUDENTS(NAME, GRADE, POINTS) VALUES(?, ?, 0);", (name, grade)
    )

    student_id = cur.lastrowid

    for event in events:
        if random.randint(0, 5) > grade_thresh[grade]:
            continue

        con.execute(
            "INSERT INTO STUDENT_ATTENDANCE(STUDENT_ID, EVENT_ID) VALUES(?, ?);",
            (
                student_id,
                event["id"],
            ),
        )

    print(name)

con.execute(
    "UPDATE STUDENTS SET POINTS = (SELECT SUM(EVENTS.POINTS) FROM EVENTS WHERE EVENTS.ID IN (SELECT EVENT_ID FROM STUDENT_ATTENDANCE WHERE STUDENT_ID = STUDENTS.ID));"
)
con.commit()
