from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate

from models import db, User
from pages.routes import pages_bp
import csi3335f2025


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.debug = True

    app.config['SECRET_KEY'] = 'a-very-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    db.init_app(app)

    with app.app_context():
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
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
