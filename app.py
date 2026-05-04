from flask import Flask
from flask_login import LoginManager
from sqlalchemy.engine import make_url

from config import Config
from models import Admin, db


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


def ensure_database_exists(database_uri):
    db_url = make_url(database_uri)
    if db_url.get_backend_name() != "postgresql":
        return

    target_db = db_url.database
    if not target_db:
        return

    admin_url = db_url.set(database="postgres")

    import psycopg2
    from psycopg2 import sql

    conn = psycopg2.connect(
        host=admin_url.host,
        port=admin_url.port,
        user=admin_url.username,
        password=admin_url.password,
        dbname=admin_url.database,
    )
    try:
        conn.set_session(autocommit=True)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
                print(f"[DB] Created PostgreSQL database: {target_db}")
    finally:
        conn.close()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    ensure_database_exists(app.config["SQLALCHEMY_DATABASE_URI"])

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    from routes import bp

    app.register_blueprint(bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
