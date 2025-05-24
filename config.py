import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_database_uri():
        if os.environ.get('FLASK_ENV') == 'production':
            return os.environ.get('DATABASE_URL') or                        'sqlite:///' + os.path.join(basedir, 'instance', 'kanban_prod.db')
        else:
            return os.environ.get('DEV_DATABASE_URL') or                        'sqlite:///' + os.path.join(basedir, 'instance', 'kanban_dev.db')

    SQLALCHEMY_DATABASE_URI = get_database_uri()

# You can add other configurations like mail, etc.
