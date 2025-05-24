import pytest
from app import create_app, db
from config import Config
import os

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite for tests
    # Or, to use a file:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_app.db')
    WTF_CSRF_ENABLED = False # Disable CSRF for testing forms if you have them (not relevant here but good practice)

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    # Optional: if using a file-based test DB, ensure it's clean before session
    # if TestConfig.SQLALCHEMY_DATABASE_URI.startswith('sqlite:///'):
    #     db_path = TestConfig.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
    #     if os.path.exists(db_path):
    #         os.remove(db_path)
    
    with app.app_context():
        db.create_all() # Create tables for the in-memory database
        yield app # Provide the app object to tests
        db.session.remove() # Clean up session
        db.drop_all() # Drop all tables after tests are done
        # Optional: if using a file-based test DB, remove it after session
        # if TestConfig.SQLALCHEMY_DATABASE_URI.startswith('sqlite:///'):
        #     if os.path.exists(db_path):
        #         os.remove(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

# Fixture to provide a clean database for each test function (if needed, otherwise use app context above)
# @pytest.fixture(scope='function')
# def init_database(app):
#     with app.app_context():
#         db.create_all()
#         yield db # Or nothing, just ensure db is clean
#         db.session.remove()
#         db.drop_all()
