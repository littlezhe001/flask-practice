from flask import Flask
from app.exts import db
from auth import auth_bp, login_manager
from routers import upload_bp, preview_bp, predict_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql+pymysql://root:@127.0.0.1:3306/biyesheji')
    db.init_app(app)

    app.secret_key = 'biyesheji secret_key'
    login_manager.init_app(app)
    app.config['UPLOAD_FOLDER'] = r'E:\毕业设计\flask\photo'

    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(preview_bp)
    app.register_blueprint(predict_bp)
    return app
