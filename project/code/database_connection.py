from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from perfect_config import db_config


def ensure_database_exists() -> None:
    """Connects to MySQL server without selecting a DB and creates it if missing."""
    password= quote_plus(db_config.password)
    base_url= (
        f"mysql+pymysql://{db_config.user}:{password}"
        f"@{db_config.host}:{db_config.port}/?charset=utf8mb4"
    )
    server_engine= create_engine(base_url, echo=False)
    
    with server_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_config.database}` CHARACTER SET utf8mb4"))
        conn.commit()


def get_engine():
    password = quote_plus(db_config.password)
    url= (
        f"mysql+pymysql://{db_config.user}:{password}"
        f"@{db_config.host}:{db_config.port}/{db_config.database}"
        f"?charset=utf8mb4"
    )
    return create_engine(url, echo=False)

def test_connection():
    try:
        ensure_database_exists()
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            print(f"[OK] Connected to: {db_name}")
            return True
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()