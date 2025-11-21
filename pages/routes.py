from flask import request, render_template, jsonify, redirect, url_for, flash

from auth import admin_required
from models import User, db
from teams import Team
from email_validator import validate_email, EmailNotValidError
from flask_login import login_required, login_user, logout_user, current_user
import random

from db_connection import get_db_connection
from pages.__init__ import pages_bp
from werkzeug.security import generate_password_hash, check_password_hash
from Player import Player


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
    return render_template('dashboard.html', user_name=username, favorite_team=favorite_team)



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
            favorite_team = User.query.filter_by(username=username).first().favorite_team
            return render_template('dashboard.html', user_name=username, favorite_team=favorite_team)
        else:
            flash("Invalid username or password")
            return redirect(url_for('pages.login'))

    return render_template('login.html')

@pages_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('pages.login'))

@pages_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    teams, years = [], []

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT DISTINCT team_name FROM teams ORDER BY team_name ASC")
            teams = [row[0] for row in cursor.fetchall()]

            cursor.execute("SELECT distinct yearid FROM teams ORDER BY yearid DESC")
            years = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

    if request.method == 'POST':
        team_name = request.form['team_name']
        year = request.form['year']
        return redirect(url_for('pages.teams', team_name=team_name, year=year))


    return render_template('search.html', teams=teams, years=years)


@pages_bp.route('/players/<playerId>')
@login_required
def players(playerId):
    conn, cursor = get_db_connection()
    player = None
    batting_career, pitching_career = [], []

    if conn and cursor:
        try:
            cursor.execute("""SELECT
                playerID, birthYear, birthMonth, birthDay, deathYear, deathMonth, deathDay,
                       nameFirst, nameLast, nameGiven, weight, height, bats, throws, debutDate, finalGameDate
                              FROM people WHERE playerID = %s""", (playerId,))
            row = cursor.fetchone()
            if row:
                player = Player()
                (player.playerId, player.birthYear, player.birthMonth, player.birthDay,
                 player.deathYear, player.deathMonth, player.deathDay, player.nameFirst,
                 player.nameLast, player.nameGiven, player.weight, player.height,
                 player.bats, player.throws, player.debut, player.finalGame) = row[:16]

            cursor.execute("""SELECT t.team_name, yearid, t.teamid, b.b_G, b.b_AB, b.b_R, b.b_H, b.b_2B, b.b_3B, b.b_HR, 
                       b.b_RBI, b.b_SB, b.b_CS, b.b_BB, b.b_SO, b.b_IBB, b.b_HBP, b.b_SH, b.b_SF, b.b_GIDP
                FROM batting b 
                         NATURAL JOIN teams t 
                WHERE playerID = %s ORDER BY yearid""", (playerId,))
            batting_career = cursor.fetchall()

            cursor.execute("""SELECT t.team_name, yearid, t.teamid, p.p_W, p.p_L, p.p_G, p.p_GS, p.p_CG, p.p_SHO, p.p_SV, p.p_IPOuts,
                    p.p_H, p.p_ER, p.p_HR, p.p_BB, p.p_SO, p.p_BAOpp, p.p_ERA, p.p_IBB, p.p_WP, p.p_HBP,
                    p.p_BK, p.p_BFP, p.p_GF, p.p_R, p.p_SH, p.p_SF, p.p_GIDP
                 FROM pitching p NATURAL JOIN teams t
                    WHERE playerid = %s
            """, (playerId,))
            pitching_career = cursor.fetchall()

        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

    return render_template('player.html', player = player,
                           batting = batting_career, pitching = pitching_career)


@pages_bp.route('/teams/<team_name>')
@login_required
def teams(team_name):
    year = request.args.get('year')
    selected_team = None
    batting_stats, pitching_stats, batting_totals, pitching_totals = [], [], [], []

    if not year:
        flash("Please select a year")
        return redirect(url_for('pages.search'))

    if year == "Pickles":
        years = get_years_for_team(team_name)
        year = random.choice(years)

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:

                cursor.execute(
                    "SELECT team_name, yearid, team_W, team_L, team_HR, park_name, team_attendance "
                    "FROM teams WHERE team_name = %s AND yearid = %s",
                    (team_name, year))
                row = cursor.fetchone()
                if row:
                    selected_team = Team(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

                batting_query = """
                SELECT p.playerid, p.nameLast, b.b_G, b.b_AB, b.b_R, b.b_H, b.b_2B, b.b_3B, b.b_HR, 
                       b.b_RBI, b.b_SB, b.b_CS, b.b_BB, b.b_SO, b.b_IBB, b.b_HBP, b.b_SH, b.b_SF, b.b_GIDP
                FROM batting b 
                         NATURAL JOIN people p 
                         NATURAL JOIN teams t 
                WHERE t.team_name = %s AND yearid = %s
                """

                pitching_query = """
                SELECT pe.playerid, pe.nameLast, p.p_W, p.p_L, p.p_G, p.p_GS, p.p_CG, p.p_SHO, p.p_SV, p.p_IPOuts,
                    p.p_H, p.p_ER, p.p_HR, p.p_BB, p.p_SO, p.p_BAOpp, p.p_ERA, p.p_IBB, p.p_WP, p.p_HBP,
                    p.p_BK, p.p_BFP, p.p_GF, p.p_R, p.p_SH, p.p_SF, p.p_GIDP
                 FROM pitching p NATURAL JOIN teams t NATURAL JOIN people pe
                    WHERE t.team_name = %s AND yearid = %s
                """

                cursor.execute(batting_query, (team_name, year))
                batting_stats = cursor.fetchall()
                cursor.execute(pitching_query, (team_name, year))
                pitching_stats = cursor.fetchall()

                if batting_stats:
                    num_cols = len(batting_stats[0])
                    for i in range(2, num_cols):
                        total = sum((row[i] or 0) for row in batting_stats)
                        batting_totals.append(total)

                if pitching_stats:
                    num_cols = len(pitching_stats[0])
                    for i in range(2, num_cols):
                        total = sum((row[i] or 0) for row in pitching_stats)
                        pitching_totals.append(total)

        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()
    return render_template(
        'team.html',
        team=selected_team,
        batting=batting_stats,
        pitching=pitching_stats,
        year=year,
        batting_totals=batting_totals,
        pitching_totals=pitching_totals
    )


@pages_bp.route('/get_years/<team>', methods=['GET', 'POST'])
def get_years(team):
    years = get_years_for_team(team)
    return jsonify(years)



def get_years_for_team(team):
    years = []
    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT yearid FROM teams WHERE team_name = %s ORDER BY yearid DESC", (team,))
            rows = cursor.fetchall()
            for row in rows:
                years.append(row[0])

        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

    return years
