from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    # FLASK_ENV is used by Flask CLI. app.debug is preferred for app.run()
    # app.debug is set based on FLASK_ENV in Config now.
    # Or directly: debug = app.config.get('DEBUG', False)
    app.run(host=host, port=port)
