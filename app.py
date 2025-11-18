from flask import Flask, render_template
from flask_login import LoginManager, current_user
from sqlalchemy.sql.functions import user

from models import db, User
from pages.routes import pages_bp


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.debug = True

    app.config['SECRET_KEY'] = 'a-very-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    db.init_app(app)

    with app.app_context():
        '''This is a command to drop the entire user table in the SQLALchemy database'''
        #db.drop_all()
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'pages.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    app.register_blueprint(pages_bp)

    return app

app = create_app()

@app.route('/')
def hello_world():
    if current_user.is_authenticated:
        favorite_team = User.query.filter_by(username=current_user.username).first().favorite_team
        return render_template('dashboard.html', user_name=current_user.username, favorite_team=favorite_team)
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
