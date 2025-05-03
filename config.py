import os
from datetime import timedelta
from environs import Env

env = Env()
env.read_env(".env")


class Config:
    OPENAI_API_KEY = env.str("OPENAI_API_KEY")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{env.str('POSTGRES_USER')}:{env.str('POSTGRES_PASSWORD')}"
        f"@{env.str('POSTGRES_HOST')}:{env.int('POSTGRES_PORT')}/{env.str('POSTGRES_DB')}"
    )
    # SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = env.str("JWT_SECRET_KEY")
    JWT_VERIFY_SUB = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    # JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    # JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=20)

    # MAIL_SERVER = 'smtp.gmail.com'
    # MAIL_PORT = 465
    # MAIL_USE_TLS = False
    # MAIL_USE_SSL = True
    # MAIL_USERNAME = env.str("MAIL_USERNAME")
    # MAIL_DEFAULT_SENDER = env.str("MAIL_USERNAME")
    # MAIL_PASSWORD = env.str("MAIL_PASSWORD")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
