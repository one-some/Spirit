import base64
import hashlib
import json
import math
import sqlite3
from os import path as os_path
from typing import Optional
import random

from flask import Flask, jsonify, redirect, render_template, request, session, url_for, flash
from werkzeug.utils import secure_filename

from pandas import read_csv as pd_read_csv
from pandas import read_excel as pd_read_excel

import audit_log
import backup
import querymaker
from config import data_path
from querymaker import Event, Student
import spiritmail

# Helper functions


def prize_from_points(points: int) -> Optional[str]:
    """Returns the highest value prize available for a user with the given points.

    Args:
        points (int): The points to be used to determine the appropriate prize.

    Returns:
        str: The name of the highest value prize available.
    """

    # Sort the prizes by points in descending order
    prizes = sorted(
        querymaker.get_prizes(), key=lambda p: p.points_required, reverse=True
    )

    # Walk through the prize list. Since they are in descending order, the first one
    # with user_points >= prize.points_required will be the highest prize the user can
    # recieve.
    for prize in prizes:
        if points >= prize.points_required:
            return prize.name

    # The poor user cannot afford any prizes. :^(
    return None


def sha256_hash(plaintext_password: str) -> str:
    """Returns the hex form of the digest of a password hashed by SHA256.

    Args:
        password (str): The plaintext password

    Returns:
        str: The SHA256 digest, in hex form.
    """
    sha256 = hashlib.sha256()
    sha256.update(plaintext_password.encode("utf-8"))
    return sha256.hexdigest()

def allowed_file(filename):
    return ('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS, filename.rsplit('.', 1)[1].lower())
# Routing

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "thisisanexamplesecretkey"
ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx", "xltx", "xltm"}


@app.route("/students")
@app.route("/leaderboard")
@app.route("/documentation")
@app.route("/audit-log")
@app.route("/inbox")
@app.route("/")
def index():
    print("\nat /\n")
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
            con.close()
            return "Username not found in database!", 404

        print("Given Hash:", given_hashed_password)

        if given_hashed_password != valid_hashed_password:
            # 403: Not authorized
            con.close()
            return "INVALID USERNAME AND PASSWORD", 403

        session["username"] = username
        role = con.execute(
            "SELECT ROLE FROM USERS WHERE NAME = ?", (username,)
        ).fetchone()[0]

        school_id = con.execute(
            "SELECT SCHOOL_ID FROM USERS WHERE NAME = ?", (session["username"],)
        ).fetchone()[0]

        con.close()
        session["role"] = role
        session["school_id"] = school_id
        print("RIGHT HERE \n", username, school_id)
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
        con.close()
    print("ALls good")
    return render_template("register.html")


@app.route("/student")
def student():
    if "username" not in session or session.get("role") != "STUDENT":
        return redirect(url_for("login"))

    con = querymaker.con()
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

    con.close()
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
            student = Student.random_from_grade(grade=criteria)

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
    out = []

    if session["role"] in ["ADMINISTRATOR", "TEACHER"]:
        # Administrators/teachers can get an overview of how many students have
        # expressed intent to attend specific events
        for event in querymaker.get_upcoming_events():
            out.append(
                {
                    **event.to_json(),
                    "interested_count": event.get_aggregate_student_interest(),
                }
            )
    elif session["role"] == "STUDENT":
        # Students need to know if they have already attended or not; this changes UI
        # state on the "I'm Going" button.
        student = Student.from_name(session["username"])
        for event in querymaker.get_upcoming_events():
            out.append(
                {
                    **event.to_json(),
                    "interested": event.get_student_interest(student.id),
                }
            )
    else:
        return jsonify({"error": "Unknown role!"}), 403

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


@app.route("/api/prize.json", methods=["POST"])
def api_new_prize():
    new_prize = {
        "name": request.json["name"],
        "desc": request.json["desc"],
        "points_required": request.json["points"],
    }

    prize_dat = querymaker.prize_dat()
    prize_dat.append(new_prize)

    with open(data_path("prizes.json"), "w") as file:
        json.dump(prize_dat, file)

    audit_log.report_event(
        user_name=session["username"],
        action="Add prize",
        details=new_prize,
    )

    return jsonify(prize_dat)


@app.route("/api/prize/<int:id>.json", methods=["PUT"])
def api_edit_prize(id: int):
    new_prize = {
        "name": request.json["name"],
        "desc": request.json["desc"],
        "points_required": request.json["points"],
    }

    prize_dat = querymaker.prize_dat()
    prize_dat[id] = new_prize

    with open(data_path("prizes.json"), "w") as file:
        json.dump(prize_dat, file)

    audit_log.report_event(
        user_name=session["username"],
        action="Edit prize",
        details=new_prize,
    )

    return jsonify(prize_dat)


@app.route("/api/prize/<int:id>.json", methods=["DELETE"])
def api_delete_prize(id: int):
    prize_dat = querymaker.prize_dat()
    old_prize = prize_dat.pop(id)

    with open(data_path("prizes.json"), "w") as file:
        json.dump(prize_dat, file)

    audit_log.report_event(
        user_name=session["username"],
        action="Delete prize",
        details=old_prize,
    )

    return jsonify(prize_dat)


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
    student, event = request.json["student_name"], request.json["event_name"]

    with querymaker.con() as con:
        exists = con.nab(
            "SELECT 1 FROM STUDENT_ATTENDANCE WHERE STUDENT_ID = (SELECT ID FROM USERS WHERE NAME = ? LIMIT 1) AND EVENT_ID = (SELECT ID FROM EVENTS WHERE NAME = ?);",
            (student, event),
        )
        if exists:
            return "Already exists!", 200

    audit_log.report_event(
        user_name=session["username"],
        action="Mark attendance",
        details={"student": student, "event": event},
    )

    try:
        with querymaker.con() as con:
            con.execute(
                "INSERT INTO STUDENT_ATTENDANCE(STUDENT_ID, EVENT_ID) VALUES((SELECT ID FROM USERS WHERE NAME = ? LIMIT 1),(SELECT ID FROM EVENTS WHERE NAME = ?));",
                (student, event),
            )

            con.commit()
        querymaker.reindex_scores()
    except sqlite3.IntegrityError:
        # Already exists
        print("integrity error")
        pass
    return "OK", 201


@app.route("/api/save_student.json", methods=["POST"])
def save_student():
    print(request.json)

    audit_log.report_event(
        user_name=session["username"],
        action="Edit student",
        details=request.json,
        allow_rollback=True,
    )

    with querymaker.con() as con:
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
        querymaker.reindex_scores()
    return "OK"


@app.route("/api/new_save_student.json", methods=["POST"])
def save_new_student():
    audit_log.report_event(
        user_name=session["username"],
        action="Add student",
        details=request.json,
    )

    
    password = "".join(random.sample(audit_log.ALPHABET, k=10))

    with querymaker.con() as con:
        con.execute(
            """INSERT INTO USERS (NAME, GRADE, POINTS, SURPLUS, EMAIL, SCHOOL_ID, ROLE, PASSWORD)
                VALUES
                    (?, ?, ?, ?, ?, ?, 'STUDENT', ?);
                """,
            (
                request.json["student_name"],
                int(request.json["student_grade"]),
                int(request.json["student_points"]),
                int(request.json["student_points"]),
                request.json["student_email"],
                session["school_id"],
                sha256_hash(password),
            ),
        )
        con.commit()
        querymaker.reindex_scores()
    # querymaker.reindex_scores()


    spiritmail.sendPassword(request.json["student_email"], request.json["student_name"], password)


    return "OK!", 201


@app.route("/api/delete_student.json", methods=["POST"])
def delete_student():
    audit_log.report_event(
        user_name=session["username"],
        action="Delete student",
        details=request.json,
        allow_rollback=True,
    )

    with querymaker.con() as con:
        con.execute(
            """DELETE FROM USERS
            WHERE ROWID = ?;""",
            (request.json["student_id"],),
        )
        con.commit()

    return


# class UploadFileForm(FlaskForm):
#     file = FileField("File")
#     submit = SubmitField("Upload File")


@app.route("/api/batch_add", methods=["POST"])
def batch_add():
    audit_log.report_event(
        user_name=session["username"], action="Batch add", allow_rollback=True
    )

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        print(file.filename)
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename)[0]:
            filename = secure_filename(file.filename)
            extension = allowed_file(file.filename)[1]

            if extension == 'csv':
                file.save(os_path.join("input", "csv.csv"))
                df = pd_read_csv("input/csv.csv")
            else:
                file.save(os_path.join("input", f"{extension}.{extension}"))
                df = pd_read_excel(f"input/{extension}.{extension}")

            df.rename(str.upper, axis="columns", inplace=True)

            print(df.columns, list(df.columns))

            
            if 'NAME' not in list(df.columns):
                flash("Error: No NAME column!")

            elif 'GRADE' not in list(df.columns):
                flash("Error: No GRADE column!")
                print("error occured")

            elif 'EMAIL' not in list(df.columns):
                flash("Error: No EMAIL column")

            elif 'POINTS' not in list(df.columns):
                df['POINTS'] = 0
                df['SURPLUS'] = 0

            if "SURPLUS" not in df.columns:
                df["SURPLUS"] = df["POINTS"]

            for key in df.columns:
                print(key)
                if key not in ['NAME', 'POINTS', 'GRADE', 'SURPLUS', 'EMAIL', 'PASSWORD']:
                    df.drop(key, axis=1, inplace=True)
            if 'PASSWORD' not in list(df.columns):
                for index, row in df.iterrows():
                    password = "".join(random.sample(audit_log.ALPHABET, k=10))
                    spiritmail.sendPassword(row['EMAIL'], row["NAME"], password)
            else:
                df["PASSWORD"] = sha256_hash(df["PASSWORD"])

            df["SCHOOL_ID"] = session["school_id"]
            df["ROLE"] = "STUDENT"

            df.dropna(inplace=True)

            with querymaker.con() as con:
                df.to_sql("USERS", con, if_exists="append", index=False)
            querymaker.reindex_scores()
            return ("", 204)


@app.route("/api/get_inbox")
def get_inbox():
    response = querymaker.get_mail(session["username"])
    print(response)
    print(jsonify(response))
    return jsonify(response)


@app.route("/api/deny", methods=["POST"])
def deny():

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

    con = querymaker.con()


    if role in ["TEACHER", "ADMINISTRATOR"]:
        print("\n", request.json, "\n")
        if con.nab(
            "SELECT SCHOOL_ID FROM USERS WHERE NAME = ?;", (session["username"],)
        ) == int(
            con.nab(
                "SELECT SCHOOL_ID FROM REQUESTS WHERE ROWID = ?",
                (request.json["request_id"],),
            )
        ):
            con.execute(
                "DELETE FROM REQUESTS WHERE ROWID = ?", (request.json["request_id"],)
            )
            print("hi :)")
            con.commit()
            return ("", 204)


@app.route("/api/accept_student_add", methods=["POST"])
def accept_student_add():
    con = querymaker.con()

    try:
        username = session["username"]
        role = session["role"]
    except KeyError:
        return redirect(url_for("login"))

    print(f"Role: {role}")
    print(f"Username: {username}")

    if not role:
        print("No role!")
        return redirect(url_for("login"))

    if role in ["TEACHER", "ADMINISTRATOR"]:
        user_school_id = int(con.nab(
            "SELECT SCHOOL_ID FROM USERS WHERE NAME = ?;",
            (session['username'],)
        ))
        requested_school_id = int(con.nab(
            'SELECT SCHOOL_ID FROM REQUESTS WHERE ROWID = ?;', (request.json["request_id"],)
        ))

        if (
            user_school_id
            == requested_school_id
        ):
            con.execute(
                "INSERT INTO USERS (NAME, GRADE, EMAIL, PASSWORD, ROLE, SCHOOL_ID) SELECT NAME, GRADE, EMAIL, PASSWORD, ROLE, SCHOOL_ID FROM REQUESTS WHERE ROWID = ?",
                (request.json["request_id"],),
            )
            con.execute(
                "DELETE FROM REQUESTS WHERE ROWID = ?", (request.json["request_id"],)
            )
            con.commit()
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


@app.route("/api/reindex_scores")
def reindex():
    querymaker.reindex_scores()
    return redirect(url_for("index"))

@app.route("/api/delete_seniors")
def delete_seniors():
    if session.get("role", None) == "ADMINISTRATOR":
        with querymaker.con() as con:
            con.execute("DELETE FROM USERS WHERE GRADE = 12")
            con.commit()
        querymaker.reindex_scores()
    return("", 204)

@app.route("/api/zero_scores")
def zero_scores():
    if session.get("role", None) == "ADMINISTRATOR":
        with querymaker.con() as con:
            con.execute("UPDATE USERS SET POINTS = 0, SURPLUS = 0")
            con.execute("DELETE FROM STUDENT_ATTENDANCE")
            con.commit()
        querymaker.reindex_scores()
    return ("", 204)

if __name__ == "__main__":
    backup.start_backup_loop()
    app.run(debug=True)
