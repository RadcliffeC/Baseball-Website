from flask import request, render_template, Blueprint, jsonify
from teams import Team
from flask_login import login_required, current_user

from csi3335f2025 import *
from werkzeug.security import generate_password_hash, check_password_hash


pages_bp = Blueprint('pages', __name__, template_folder='templates')
@pages_bp.route('/register', methods=['GET', 'POST'])
def register():
    user_name = 'TEST'
    return render_template('dashboard.html',
                           user_name=user_name,)

@pages_bp.route('/login', methods=['GET', 'POST'])
def login():
    return register()

@pages_bp.route('/search', methods=['GET', 'POST'])
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

                try:
                    cursor.execute("SELECT team_W, team_L, team_HR, park_name, team_attendance FROM teams WHERE team_name = %s AND yearid = %s", (team,year))
                    rows = cursor.fetchall()
                    wins = rows[0][0]
                    losses = rows[0][1]
                    team_hr = rows[0][2]
                    park = rows[0][3]
                    attendance = rows[0][4]

                    selected_team = Team(team, year, wins,
                                         losses, team_hr, park, attendance)
                except Exception as e:
                    print(e)



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
            cursor.execute("SELECT yearid FROM teams WHERE team_name = %s", (team))
            rows = cursor.fetchall()
            for row in rows:
                years.append(row[0])

        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

    return years
