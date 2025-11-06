from flask import request, render_template, Blueprint, jsonify, redirect, url_for, flash
from models import User, db
from teams import Team
from email_validator import validate_email, EmailNotValidError
from flask_login import login_required, login_user, logout_user

from db_connection import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

pages_bp = Blueprint('pages', __name__, template_folder='templates')


def register_submit(username, password, email, favorite_team):
    try:
        validated = validate_email(email)
        email = validated.normalized
    except EmailNotValidError as e:
        flash(str(e), "error")
        return redirect(url_for("pages.register"))

    if db.session.query(User).filter_by(email=email).first():
        flash("Email already registered")
        return redirect(url_for("pages.register"))

    if db.session.query(User).filter_by(username=username).first():
        flash("Username already registered")
        return redirect(url_for("pages.register"))


    password_hash = generate_password_hash(password)
    user = User(username=username, password=password_hash, email=email, favorite_team=favorite_team)

    db.session.add(user)
    db.session.commit()

    login_user(user, True)
    return render_template('dashboard.html', user_name=username)


@pages_bp.route('/register', methods=['GET', 'POST'])
def register():
    teams = []
    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute(
                "SELECT DISTINCT team_name FROM teams ORDER BY team_name ASC"
            )
            teams = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        favorite_team = request.form['favorite_team']
        return register_submit(username, password, email, favorite_team)

    return render_template('register.html', teams=teams)

@pages_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return render_template('dashboard.html', user_name=username)
        else:
            flash("Invalid username or password")
            return redirect(url_for('pages.login'))

    return render_template('login.html')

@pages_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('pages.login'))

@login_required
@pages_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    teams, years = [], []
    selected_team = None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT distinct team_name FROM teams ORDER BY team_name ASC")
            teams = [row[0] for row in cursor.fetchall()]

            cursor.execute("SELECT distinct yearid FROM teams ORDER BY yearid DESC")
            years = [row[0] for row in cursor.fetchall()]

            if request.method == 'POST':
                team = request.form['team_name']
                year = request.form['year']
                cursor.execute(
                    "SELECT team_W, team_L, team_HR, park_name, team_attendance "
                    "FROM teams WHERE team_name = %s AND yearid = %s",
                    (team, year))
                row = cursor.fetchone()
                if row:
                    selected_team = Team(team, year, *row)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()


    return render_template('search.html', teams=teams, years=years, team=selected_team)

@pages_bp.route('/get_years/<team>', methods=['GET', 'POST'])
def get_years(team):
    years = get_years_for_team(team)
    return jsonify(years)



def get_years_for_team(team):
    years = []
    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT yearid FROM teams WHERE team_name = %s ORDER BY yearid DESC", (team))
            rows = cursor.fetchall()
            for row in rows:
                years.append(row[0])

        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

    return years
