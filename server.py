import query
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def index():
    return "HEY INDEX"

@app.route("/students.json")
def students():
    sort = query.Sort.from_string(request.args.get("sort", "name_desc"))

    try:
        limit = min(300, int(request.args.get("limit")))
    except (ValueError, TypeError):
        limit = 100

    return jsonify(
        query.get_students(limit=limit, sort=sort)
    )
 
if __name__ == "__main__":
    app.run()
