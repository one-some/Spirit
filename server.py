import base64
import math
import json
import sqlite3
import hashlib
from config import config, data_path
from pandas import read_csv as pd_read_csv
from flask import Flask, jsonify, request, render_template, redirect, url_for, session

import backup
import audit_log
import querymaker
from querymaker import Student, Event

# from pandas import DataFrame
# from werkzeug.utils import secure_filename
from os import path as os_path

# from flask_wtf import FlaskForm
# from wtforms import FileField, SubmitField

# Helper functions


def prize_from_points(points: int) -> str:
    prizes = sorted(
        querymaker.get_prizes(), key=lambda p: p.points_required, reverse=True
    )
    print(prizes)

    for prize in prizes:
        if points >= prize.points_required:
            return prize.name
    return None


def sha256_hash(
    password: str,
):  # hashes the password with hashlib, a default library. I don't know why the weird way of doing it.
    sha256 = hashlib.sha256()
    password = password.encode("utf-8")
    sha256.update(password)
    return sha256.hexdigest()


# Routing

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "thisisanexamplesecretkey"


@app.route("/students")
@app.route("/leaderboard")
@app.route("/documentation")
@app.route("/audit-log")
@app.route("/inbox")
@app.route("/")
def index():
    print("\nat /\n")
    con = querymaker.con()

    try:
        username = session["username"]
        role = session["role"]
    except KeyError:
        return redirect(url_for("login"))

    print(f"Role: {role}")
    print(f"Username: {username}")

    if not role:
        print("No role!?!?! what???")
        return redirect(url_for("login"))

    if role in ["TEACHER", "ADMINISTRATOR"]:
        return render_template("index.html")

    return redirect(url_for("student"))


@app.route("/login", methods=["GET", "POST"])
def login():
    print("\nat login\n")
    if request.method == "POST":
        try:
            username = request.form["username"]
        except KeyError:
            # 400: Bad request
            return "No username given!", 400

        try:
            # Be careful with this!
            given_plaintext_password = request.form["password"]
        except KeyError:
            return "No password given!", 400
        given_hashed_password = sha256_hash(given_plaintext_password)

        con = querymaker.con()

        try:
            valid_hashed_password = con.execute(
                "SELECT PASSWORD FROM USERS WHERE NAME = ?", (username,)
            ).fetchone()[0]
        except TypeError:
            # TypeError: None is not subscriptable, as fetchone()
            # will return None if it has nothing to fetch
            return "Username not found in database!", 404

        print("Given Hash:", given_hashed_password)

        if given_hashed_password != valid_hashed_password:
            # 403: Not authorized
            return "INVALID USERNAME AND PASSWORD", 403

        session["username"] = username
        role = con.execute(
            "SELECT ROLE FROM USERS WHERE NAME = ?", (username,)
        ).fetchone()[0]
        session["role"] = role
        # We can assume that this query will succeed since the last
        # one confirmed there's a user with that name in the db

        if role == "STUDENT":
            return redirect(url_for("student"))
        return redirect(url_for("index"))

    if "username" in session:
        if session.get("role") in ["TEACHER", "ADMINISTRATOR"]:
            return redirect(url_for("index"))

        print(
            "\n",
            session["role"],
            " at student\n",
        )
        return redirect(url_for("student"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        print(
            request.form.get("Create", "no value"),
            request.form.get("Create", "no value") == "on",
        )
        con = querymaker.con()

        a = int(request.form["school-id"])
        atype = type(a)
        try:
            c = con.execute(
                "SELECT SCHOOL_ID FROM SCHOOLS WHERE SCHOOL_ID = ?",
                (request.form["school-id"],),
            ).fetchall()[0][0]
        except:
            c = None
        ctype = type(c)
        n = "\n"

        print(n, a, n, atype, n, c, n, ctype, n, a == c, n)

        if request.form.get("Create", False) != "on":
            print(request.form)

            con.execute(
                "INSERT INTO REQUESTS(OPERATION, NAME, EMAIL, PASSWORD, SCHOOL_ID, ROLE, GRADE) VALUES ('ADD', ?, ?, ?, ?, ?, ?)",
                (
                    request.form["username"],
                    request.form["email"],
                    sha256_hash(request.form["password"]),
                    request.form["school-id"],
                    request.form["role"],
                    request.form.get("grade", None),
                ),
            )
            con.commit()
            # con.execute("")

        elif (
            request.form.get("Create", False) == "on"
            and int(request.form["school-id"]) != c
        ):
            con.execute(
                "INSERT INTO USERS (NAME, EMAIL, PASSWORD, SCHOOL_ID, ROLE, GRADE) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    request.form["username"],
                    request.form["email"],
                    sha256_hash(request.form["password"]),
                    request.form["school-id"],
                    request.form["role"],
                    None,
                ),
            )
            con.commit()
            con.execute(
                "INSERT INTO SCHOOLS (SCHOOL_ID, SCHOOL_NAME) VALUES (?, ?)",
                (
                    request.form["school-id"],
                    request.form["school-name"],
                ),
            )
            con.commit()
            print("went through for some reason")
    return render_template("register.html")


@app.route("/student")
def student():
    if "username" not in session or session.get("role") != "STUDENT":
        return redirect(url_for("login"))

    con = querymaker.Connection()
    points = con.nab("SELECT POINTS FROM USERS WHERE NAME = ?", (session["username"],))

    POINT_GOAL_INCREMENTS = 15000
    point_goal = POINT_GOAL_INCREMENTS * math.ceil(points / POINT_GOAL_INCREMENTS)

    student = Student.from_name(session["username"])
    attended_events = con.nab(
        "SELECT COUNT() FROM STUDENT_ATTENDANCE WHERE STUDENT_ID = ?;", (student.id,)
    )

    missed_events = con.nab(
        "SELECT COUNT() FROM EVENTS WHERE NOT EXISTS(SELECT 1 FROM STUDENT_ATTENDANCE WHERE EVENT_ID = ID AND STUDENT_ID = ?);",
        (student.id,),
    )

    distance_to_first = (
        con.nab("SELECT POINTS FROM STUDENTS ORDER BY POINTS DESC LIMIT 1;")
        - student.points
    )

    return render_template(
        "student.html",
        pretty_points=f"{points:,}",
        pretty_point_goal=f"{point_goal:,}",
        progress_percent=(points / point_goal) * 100,
        pretty_attended_events=f"{attended_events:,}",
        pretty_missed_events=f"{missed_events:,}",
        pretty_distance_to_first=f"{distance_to_first:,}",
        b64encode=lambda x: base64.b64encode(x.encode("utf-8")).decode("utf-8"),
    )


@app.route("/logout", methods=["GET", "POST"])
def logout():
    print(session)
    session.pop("username", None)
    print(session)
    return redirect(url_for("login"))


@app.route("/event/<int:event_id>")
def event(event_id: int):
    event = Event.from_id(event_id).to_json()
    return render_template("event.html", event=event)


@app.route("/api/students.json")
def api_students():
    query = request.args.get("q", None)
    grade_filters = {}
    for grade in querymaker.GRADES:
        grade_filters[grade] = request.args.get(f"show_{grade}th", "true") == "true"

    sort = querymaker.Sort.from_string(request.args.get("sort", "name_desc"))
    score_condition = request.args.get("scorecondition")
    try:
        limit = min(300, int(request.args.get("limit")))
    except (ValueError, TypeError):
        limit = 100
    return jsonify(
        querymaker.get_students(
            limit=limit,
            sort=sort,
            score_condition=score_condition,
            query=query,
            grade_filters=grade_filters,
        )
    )


@app.route("/api/draw_results.json")
def api_draw_results():
    winners = {}

    for criteria in ["top", 9, 10, 11, 12]:
        if criteria == "top":
            student = querymaker.get_students(
                limit=1, sort=querymaker.Sort.POINTS_DESC
            )[0]
        else:
            # Criteria is grade number
            student = querymaker.get_random_student(grade=criteria)

        winners[str(criteria)] = {
            "student": student,
            "prize": prize_from_points(student.points),
        }

    audit_data = {winner: result["student"] for winner, result in winners.items()}
    audit_log.report_event(
        user_name=session["username"], action="Draw results", details=audit_data
    )
    return jsonify(winners)


@app.route("/api/suggest.json")
def api_suggestions():
    query = request.args.get("q")
    print(query)
    return jsonify(querymaker.get_students_matching(query))


@app.route("/api/events.json")
def api_events():
    if session["role"] != "STUDENT":
        out = []
        for event in querymaker.get_upcoming_events():
            out.append({
                **event.__dict__,
                "interested_count": event.get_aggregate_student_interest()
            })
        return jsonify(out)

    student = Student.from_name(session["username"])
    out = []
    for event in querymaker.get_upcoming_events():
        out.append({
            **event.__dict__,
            "interested": event.get_student_interest(student.id)
        })
    print([x["interested"] for x in out])

    return jsonify(out)


@app.route("/api/prizes.json")
def api_prizes():
    return jsonify(querymaker.get_prizes())


@app.route("/api/stats.json")
def api_stats():
    return jsonify(querymaker.get_aggregate_stats())


@app.route("/api/audit_log.json")
def get_audit_log():
    con = querymaker.con()

    dat = []

    for row in con.execute(
        "SELECT rowid, time, user, action, details, rollback_id FROM audit_log ORDER BY time DESC LIMIT 100;"
    ):
        dat.append(
            {
                "event_id": row[0],
                "time": row[1],
                "user": row[2],
                "action": row[3],
                "details": json.loads(row[4]) if row[4] else None,
                "has_checkpoint": bool(row[5]),
            }
        )

    return jsonify(dat)


@app.route("/api/set_prizes.json", methods=["POST"])
def api_set_prizes():
    new_dat = []
    for prize in request.json:
        new_dat.append(
            {
                "name": prize["name"],
                "desc": prize["desc"],
                "points_required": prize["points"],
            }
        )

    with open(data_path("prizes.json"), "w") as file:
        json.dump(new_dat, file)

    audit_log.report_event(
        user_name=session["username"],
        action="Set prizes",
        details=new_dat,
    )

    return "Ok! :)"


@app.route("/api/create_event.json", methods=["POST"])
def api_create_event():
    print(request.json)

    audit_log.report_event(
        user_name=session["username"],
        action="Create event",
        details=request.json,
        allow_rollback=True,
    )

    con = querymaker.con()
    con.execute(
        "INSERT INTO EVENTS(NAME, LOCATION, DESCRIPTION, POINTS, TIME_START, TIME_END) VALUES(?, ?, ?, ?, ?, ?);",
        (
            request.json["name"],
            request.json["location"],
            request.json["desc"],
            int(request.json["points"]),
            request.json["time_start"],
            request.json["time_end"],
        ),
    )
    con.commit()

    return "Ok! :)"


@app.route("/api/attend.json", methods=["POST"])
def api_attend():
    print(request.json)
    con = querymaker.con()
    student, event = request.json["student_name"], request.json["event_name"]

    try:
        con.execute(
            "INSERT INTO STUDENT_ATTENDANCE(STUDENT_ID, EVENT_ID) VALUES((SELECT ID FROM USERS WHERE NAME = ? LIMIT 1),(SELECT ID FROM EVENTS WHERE NAME = ?));",
            (student, event),
        )

        audit_log.report_event(
            user_name=session["username"],
            action="Mark attendance",
            details={"student": student, "event": event},
        )

        con.commit()
        querymaker.reindex_scores()
    except sqlite3.IntegrityError:
        # Already exists
        pass
    return "Ok! :)"


@app.route("/api/save_student.json", methods=["POST"])
def save_student():
    print(request.json)

    audit_log.report_event(
        user_name=session["username"],
        action="Edit student",
        details=request.json,
        allow_rollback=True,
    )

    con = querymaker.con()
    con.execute(
        """UPDATE USERS
            SET NAME = ?,
               GRADE = ?,
               SURPLUS = ? - (POINTS - SURPLUS),
               POINTS = ?
            WHERE ROWID = ?;
            """,
        (
            request.json["student_name"],
            int(request.json["student_grade"]),
            int(request.json["student_points"]),
            int(request.json["student_points"]),
            request.json["student_id"],
        ),
    )

    con.commit()

    return "what is the point of these"


@app.route("/api/new_save_student.json", methods=["POST"])
def save_new_student():
    print(request.json)

    audit_log.report_event(
        user_name=session["username"],
        action="Add student",
        details=request.json,
    )

    con = querymaker.con()
    con.execute(
        """INSERT INTO USERS (NAME, GRADE, POINTS, SURPLUS)
            VALUES
                (?, ?, ?, ?);
            """,
        (
            request.json["student_name"],
            int(request.json["student_grade"]),
            int(request.json["student_points"]),
            int(request.json["student_points"]),
        ),
    )

    con.commit()

    # querymaker.reindex_scores()

    return "Workjjing?"


@app.route("/api/delete_student.json", methods=["POST"])
def delete_student():
    audit_log.report_event(
        user_name=session["username"],
        action="Delete student",
        details=request.json,
        allow_rollback=True,
    )

    con = querymaker.con()
    con.execute(
        """DELETE FROM USERS
           WHERE ROWID = ?;""",
        (request.json["student_id"],),
    )

    con.commit()

    return "dude idk"


# class UploadFileForm(FlaskForm):
#     file = FileField("File")
#     submit = SubmitField("Upload File")


@app.route("/api/batch_add", methods=["POST"])
def batch_add():
    audit_log.report_event(
        user_name=session["username"], action="Batch add", allow_rollback=True
    )

    con = querymaker.con()
    # df = pd.read_excel(request, sheet_name=None)
    f = request.files["file"]
    # filename = secure_filename(f.filename)
    f.save(os_path.join("input", "csv.csv"))
    df = pd_read_csv("input/csv.csv")
    df.rename(str.upper, axis="columns", inplace=True)
    print("\n", df, "\n")
    if "SURPLUS" not in df.columns:
        df["SURPLUS"] = df["POINTS"]
    df.to_sql("USERS", con, if_exists="append", index=False)
    return ("", 204)


@app.route("/api/get_inbox")
def get_inbox():
    response = querymaker.get_mail(session["username"])
    print(response)
    print(jsonify(response))
    return jsonify(response)


@app.route("/api/deny", methods=["POST"])
def deny():
    c = querymaker.con()

    try:
        username = session["username"]
        role = session["role"]
    except KeyError:
        return redirect(url_for("login"))

    print(f"Role: {role}")
    print(f"Username: {username}")

    if not role:
        print("No role!?!?! what???")
        return redirect(url_for("login"))

    if role in ["TEACHER", "ADMINISTRATOR"]:
        print("\n", request.json, "\n")
        if c.execute(
            f"SELECT SCHOOL_ID FROM USERS WHERE NAME = \"{session['username']}\""
        ).fetchone()[0] == int(
            c.execute(
                f"SELECT SCHOOL_ID FROM REQUESTS WHERE ROWID = ?",
                (request.json["request_id"],),
            ).fetchone()[0]
        ):
            c.execute(
                "DELETE FROM REQUESTS WHERE ROWID = ?", (request.json["request_id"],)
            )
            print("hi :)")
            c.commit()
            return ("", 204)


@app.route("/api/accept_student_add", methods=["POST"])
def accept_student_add():
    c = querymaker.con()

    try:
        username = session["username"]
        role = session["role"]
    except KeyError:
        return redirect(url_for("login"))

    print(f"Role: {role}")
    print(f"Username: {username}")

    if not role:
        print("No role!?!?! what???")
        return redirect(url_for("login"))

    if role in ["TEACHER", "ADMINISTRATOR"]:
        a = c.execute(
            f"SELECT SCHOOL_ID FROM USERS WHERE NAME = \"{session['username']}\""
        ).fetchone()[0]
        b = c.execute(
            f'SELECT SCHOOL_ID FROM REQUESTS WHERE ROWID = \'{request.json["request_id"]}\''
        ).fetchone()[0]
        n = "\n\n"
        print(
            "HERE",
            n,
            "a: ",
            a,
            n,
            "type of a: ",
            type(a),
            n,
            "b: ",
            b,
            n,
            "type of b: ",
            type(b),
            n,
        )

        if (
            c.execute(
                f"SELECT SCHOOL_ID FROM USERS WHERE NAME = \"{session['username']}\""
            ).fetchone()[0]
            == c.execute(
                f'SELECT SCHOOL_ID FROM REQUESTS WHERE ROWID = \'{request.json["request_id"]}\''
            ).fetchone()[0]
        ):
            c.execute(
                "INSERT INTO USERS (NAME, GRADE, EMAIL, PASSWORD, ROLE, SCHOOL_ID) SELECT NAME, GRADE, EMAIL, PASSWORD, ROLE, SCHOOL_ID FROM REQUESTS WHERE ROWID = ?",
                (request.json["request_id"],),
            )
            c.execute(
                "DELETE FROM REQUESTS WHERE ROWID = ?", (request.json["request_id"],)
            )
            c.commit()
        return ("", 204)


@app.route("/api/events/<int:event_id>/interest.json", methods=["POST"])
def set_event_interest(event_id: int):
    if session.get("role") != "STUDENT" or "username" not in session:
        return ("Only students may perform this action", 403)

    try:
        is_interested = bool(request.json["interested"])
    except KeyError:
        return ("Missing args", 400)

    event = Event.from_id(event_id)
    student = Student.from_name(session["username"])
    event.set_student_interest(student.id, is_interested)
    return ("", 201)


@app.route("/api/events/<int:event_id>/interest.json", methods=["GET"])
def get_event_interest(event_id: int):
    if session.get("role") != "STUDENT" or "username" not in session:
        return ("Only students may perform this action", 403)
    
    event = Event.from_id(event_id)
    student = Student.from_name(session["username"])
    return jsonify(event.get_student_interest(student.id))


if __name__ == "__main__":
    backup.start_backup_loop()
    app.run(debug=True)
