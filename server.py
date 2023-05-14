import json
import backup
from flask import Flask, jsonify, request, render_template
import sqlite3
import querymaker
from config import config, data_path

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


# Routing

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
@app.route("/students")
@app.route("/leaderboard")
def index():
    return render_template("index.html")


@app.route("/event/<int:event_id>")
def event(event_id: int):
    event = querymaker.get_event(event_id).to_json()

    return render_template("event.html", event=event)


@app.route("/api/students.json")
def api_students():
    sort = querymaker.Sort.from_string(request.args.get("sort", "name_desc"))

    try:
        limit = min(300, int(request.args.get("limit")))
    except (ValueError, TypeError):
        limit = 100

    return jsonify(querymaker.get_students(limit=limit, sort=sort))


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

    return jsonify(winners)


@app.route("/api/suggest.json")
def api_suggestions():
    query = request.args.get("q")
    print(query)
    return jsonify(querymaker.get_students_matching(query))


@app.route("/api/events.json")
def api_events():
    return jsonify(querymaker.get_upcoming_events())


@app.route("/api/prizes.json")
def api_prizes():
    return jsonify(querymaker.get_prizes())


@app.route("/api/stats.json")
def api_stats():
    return jsonify(querymaker.get_aggregate_stats())


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

    return "Ok! :)"


@app.route("/api/create_event.json", methods=["POST"])
def api_create_event():
    print(request.json)

    con = querymaker.con()

    con.execute(
        "INSERT INTO EVENTS(NAME, LOCATION, DESCRIPTION, POINTS, TIME_START, TIME_END) VALUES(?, ?, ?, ?, ?, ?);",
        (
            request.json["name"],
            request.json["location"],
            request.json["desc"],
            request.json["points"],
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

    try:
        con.execute(
            "INSERT INTO STUDENT_ATTENDANCE(STUDENT_ID, EVENT_ID) VALUES((SELECT ID FROM STUDENTS WHERE NAME = ? LIMIT 1),(SELECT ID FROM EVENTS WHERE NAME = ?));",
            (
                request.json["student_name"],
                request.json["event_name"],
            ),
        )
    except sqlite3.IntegrityError:
        # Already exists
        pass

    con.commit()
    querymaker.reindex_scores()

    return "Ok! :)"

@app.route("/api/save_student.json", methods=["POST"])
def save_student():
    print(request.json)
    con = querymaker.con()
    con.execute(
        '''UPDATE STUDENTS
           SET NAME = ?,
               GRADE = ?,
               POINTS = ?
            WHERE ROWID = ?;
            ''',
        (
            request.json["student_name"],
            request.json["student_grade"],
            request.json["student_points"],
            request.json["student_id"],
        )
    )

@app.route("/api/new_save_student.json", methods=["POST"])
def save_new_student():
    print(request.json)
    con = querymaker.con()
    con.execute(
        '''INSERT INTO STUDENTS (NAME, GRADE, POINTS)
            VALUES
                (?, ?, ?);
            ''',
        (
            request.json["student_name"],
            request.json["student_grade"],
            request.json["student_points"],
        )
    )

    con.commit()

    # querymaker.reindex_scores()
    
    return "Workjjing?"


if __name__ == "__main__":
    backup.start_backup_loop()
    app.run()
