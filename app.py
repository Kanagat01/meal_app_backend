from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from models import db, bcrypt
from routes import *


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = Token.query.filter_by(jti=jti).first()
        if not token:
            return False
        return token.revoked

    db.init_app(app)
    bcrypt.init_app(app)

    Migrate(app, db)
    app.register_blueprint(auth_bp)
    app.register_blueprint(meals_bp)
    app.register_blueprint(profile_bp)

    return app
