import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQL_ALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQL_ALCHEMY_TRACK_MODIFICATIONS')
    SESSION_TYPE = os.environ.get('SESSION_TYPE')
    PERMANENT_SESSION_LIFETIME = timedelta(int(os.environ.get('PERMANENT_SESSION_LIFETIME')))
    SESSOIN_PERMANENT = os.environ.get('SESSION_PERMANENT')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = "Oriah Web Studios, ramotsepanem@gmail.com"
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'uploads', 'projects')





