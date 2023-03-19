import random
import sqlite3

STUDENT_COUNT = 1629
con = sqlite3.connect("data/spirit.db")

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


def get_name():
    return " ".join([random.choice(first_names), random.choice(last_names)])


for _ in range(STUDENT_COUNT):
    name = get_name()
    points = random.randint(0, 3000)
    con.execute("INSERT INTO STUDENTS(NAME, POINTS) VALUES(?, ?);", (name, points))
    print(name, points)
con.commit()
