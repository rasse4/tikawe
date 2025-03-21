import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    db.execute("INSERT INTO visits (visited_at) VALUES (datetime('now'))")
    result = db.query("SELECT COUNT(*) FROM visits")
    countvisits = result[0][0]
    messages = db.query("SELECT content FROM messages")
    count = len(messages)
    return render_template("index.html", count=count, countvisits=countvisits, messages=messages)

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    db.execute("INSERT INTO messages (content) VALUES (?)", [content])
    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"


@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")

@app.route("/modify_star")
def modify_star():
    return render_template("modify_star.html")

@app.route("/create_star", methods=["GET", "POST"])
def create_star():
    star_name = request.form["starname"]
    star_content = request.form["starcontent"]

    sql = """INSERT INTO star (name, content) VALUES (?,?)"""
    db.execute(sql, [star_name, star_content])
    return redirect("/")


@app.route("/modify", methods=["GET","POST"])
def modify():
    types = db.query("SELECT name FROM type")
    stars = db.query("SELECT name FROM star")
    methods = db.query("SELECT name FROM method")

    return render_template("/modify.html", types=types, stars=stars, methods=methods)


@app.route("/create_planet", methods=["GET", "POST"])
def create_planet():
    planet_name = request.form["planetname"]
    planet_content = request.form["planetcontent"]
    planet_types = request.form["planettypes"]
    planet_star = request.form["planetstar"]
    planet_date = request.form["planetdate"]
    user_id = session["user_id"]

    sql = "INSERT INTO planet (name, content, discovery, user_id) VALUES (?,?,?,?)"
    db.execute(sql, [planet_name, planet_content, planet_date, user_id])

    sql = ("SELECT id FROM star WHERE name = ?")
    result = db.query(sql, [planet_star])
    star_id = result[0]







    return redirect("/")

@app.route("/ownpage")
def ownpage():
    return render_template("ownpage.html")