from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure the instance folder exists
    # The instance_path is now correctly determined by Flask
    instance_path = app.instance_path 
    try:
        os.makedirs(instance_path)
    except OSError:
        pass # Already exists or other error

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models here to ensure they are registered with SQLAlchemy
    from app import models 

    # Register blueprints here
    from app.routes.projects_bp import projects_api_bp
    from app.routes.stages_bp import stages_api_bp
    from app.routes.tasks_bp import tasks_api_bp
    from app.routes.subtasks_bp import subtasks_api_bp

    app.register_blueprint(projects_api_bp, url_prefix='/api')
    app.register_blueprint(stages_api_bp, url_prefix='/api')
    app.register_blueprint(tasks_api_bp, url_prefix='/api')
    app.register_blueprint(subtasks_api_bp, url_prefix='/api')
    
    # A simple test route (can be moved or kept here)
    @app.route('/hello')
    def hello():
        return "你好，看板后端已启动！(Hello, Kanban Backend is Running!)"

    return app
