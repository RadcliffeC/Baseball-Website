from flask import Flask, render_template, Blueprint
from pages.routes import pages_bp
import csi3335f2025


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')

    app.register_blueprint(pages_bp)

    return app

app = create_app()

@app.route('/')
def hello_world():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
