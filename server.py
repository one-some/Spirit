import querymaker
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/students.json")
def students():
    sort = querymaker.Sort.from_string(request.args.get("sort", "name_desc"))

    try:
        limit = min(300, int(request.args.get("limit")))
    except (ValueError, TypeError):
        limit = 100

    return jsonify(
        querymaker.get_students(limit=limit, sort=sort)
    )

@app.route("/api/suggest.json")
def suggestions():
    query = request.args.get("q")
    print(query)
    return jsonify(querymaker.get_students_matching(query))
 
if __name__ == "__main__":
    app.run()
